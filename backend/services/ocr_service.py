from PIL import Image
import io
import re
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import google.generativeai as genai
from decouple import config

class OCRService:
    def __init__(self):
        # Gemini API setup - python-decouple ile .env dosyasından oku
        self.gemini_api_key = config('GEMINI_API_KEY', default=None)
        
        print(f"🔍 Debug - API Key: {self.gemini_api_key[:10] if self.gemini_api_key else 'None'}...")
        
        if not self.gemini_api_key or self.gemini_api_key == 'your-gemini-api-key-here':
            raise ValueError("GEMINI_API_KEY is required! Please set it in your .env file")
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print(f"🤖 Gemini API configured successfully with model: gemini-1.5-flash")
    
    def process_invoice(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Gemini API ile fatura görselini analiz eder ve veri çıkarır
        """
        try:
            return self.process_with_gemini(image_bytes)
        except Exception as e:
            print(f"❌ Gemini OCR processing failed: {str(e)}")
            return {
                "error": f"Gemini OCR processing failed: {str(e)}",
                "raw_text": "",
                "extracted_data": {},
                "processing_timestamp": datetime.utcnow().isoformat()
            }

    def process_with_gemini(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Gemini API ile fatura işleme
        """
        try:
            # Image'ı PIL formatına çevir
            image = Image.open(io.BytesIO(image_bytes))
            
            # Gemini için optimize edilmiş prompt
            prompt = """
Bu Türkçe faturayı analiz et ve aşağıdaki JSON formatında bilgileri çıkar:

{
    "company_name": "şirket_adı",
    "invoice_number": "fatura_numarası", 
    "invoice_date": "fatura_tarihi",
    "total_amount": "toplam_tutar",
    "tax_amount": "kdv_tutarı",
    "tax_rate": "kdv_oranı"
}

KURALLAR:
1. ŞİRKET ADI: Faturanın EN ÜST satırında bulunan şirket ismi
2. FATURA NO: "FATURA NO:", "FATURA NUMARASI:", "NO:" yazısının yanındaki değer (harf+sayı olabilir)
3. TARİH: Fatura tarihi (DD.MM.YYYY veya DD/MM/YYYY formatında)
4. TOPLAM TUTAR: "TOPLAM", "GENEL TOPLAM" yazısının yanındaki tutar (sadece sayı+virgül/nokta, TL olmadan)
5. KDV TUTARI: "KDV", "K.D.V" yazısının yanındaki tutar (sadece sayı+virgül/nokta, TL olmadan)
6. KDV ORANI: KDV oranını bulmak için şu alanları dikkatli incele:
   - "%18", "%20", "18%", "20%" gibi açık oran yazıları
   - "KDV %18", "KDV %20", "K.D.V %18" gibi KDV yanındaki oranlar
   - Tablolarda KDV sütununda yazılı oranlar
   - "18 KDV", "20 KDV" gibi sayı+KDV formatları
   - Fatura detaylarında ürün bazında yazılı KDV oranları
   - Türkiye'de yaygın KDV oranları: 0, 1, 8, 18, 20
   - Sadece sayıyı döndür (% işareti olmadan)

ÖNEMLİ KDV ORANI DETAYLARI:
- Eğer birden fazla KDV oranı varsa, en yüksek oranı al
- Eğer KDV oranı bulunamazsa ama KDV tutarı varsa, hesapla: (KDV tutarı / (toplam tutar - KDV tutarı)) * 100
- KDV oranı genellikle 0, 1, 8, 18 veya 20 olur
- Tablolarda, sütun başlıklarında veya satır sonlarında olabilir

ÖNEMLİ SAYI FORMATLAMA KURALLARI:
- Binlik ayırıcı: nokta (.) - 1.000, 15.750
- Ondalık ayırıcı: virgül (,) - 1.000,50, 15.750,25
- Para birimi sembolleri kullanma (TL, ₺, $)
- Sadece sayıları döndür

Bulunamayan bilgiler için null kullan.
Sadece JSON yanıtı ver, başka açıklama ekleme.
"""

            # Gemini'ye gönder
            response = self.model.generate_content([prompt, image])
            
            print(f"🤖 Gemini Raw Response: {response.text}")
            
            # JSON parse et
            try:
                # JSON'u temizle ve parse et
                json_text = response.text.strip()
                if json_text.startswith('```json'):
                    json_text = json_text.replace('```json', '').replace('```', '').strip()
                elif json_text.startswith('```'):
                    json_text = json_text.replace('```', '').strip()
                
                extracted_data = json.loads(json_text)
                
                # KDV oranı için ek kontrol - JSON'da null ise fallback kullan
                if not extracted_data.get("tax_rate"):
                    extracted_data["tax_rate"] = self.extract_kdv_rate_from_text(response.text)
                    
                    # Eğer hala bulunamadıysa, KDV tutarı ve toplam tutardan hesapla
                    if not extracted_data["tax_rate"] and extracted_data.get("tax_amount") and extracted_data.get("total_amount"):
                        calculated_rate = self.calculate_kdv_rate_from_amounts(
                            extracted_data["tax_amount"], 
                            extracted_data["total_amount"]
                        )
                        if calculated_rate:
                            extracted_data["tax_rate"] = calculated_rate
                            
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                # Fallback: regex ile çıkar
                extracted_data = self.extract_from_gemini_text(response.text)
            
            # Skorla
            score = self.calculate_extraction_score(extracted_data)
            
            print(f"✅ Gemini Extracted Data: {extracted_data}")
            print(f"📊 Extraction Score: {score}")
            
            # KDV oranı özel log
            if extracted_data.get("tax_rate"):
                print(f"🎯 KDV Oranı Bulundu: {extracted_data['tax_rate']}%")
            else:
                print(f"⚠️ KDV Oranı Bulunamadı")
            
            return {
                "raw_text": response.text,
                "extracted_data": extracted_data,
                "extraction_score": score,
                "processing_method": "gemini",
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Gemini processing failed: {str(e)}")
            raise e

    def extract_from_gemini_text(self, text: str) -> Dict[str, Any]:
        """
        Gemini'nin JSON formatında olmayan yanıtından veri çıkarır
        """
        extracted = {
            "company_name": None,
            "invoice_number": None,
            "invoice_date": None,
            "total_amount": None,
            "tax_amount": None,
            "tax_rate": None
        }
        
        # Basit regex'lerle çıkar
        patterns = {
            "company_name": r'company_name["\s:]+([^,\n"]+)',
            "invoice_number": r'invoice_number["\s:]+([^,\n"]+)',
            "invoice_date": r'invoice_date["\s:]+([^,\n"]+)',
            "total_amount": r'total_amount["\s:]+([^,\n"]+)',
            "tax_amount": r'tax_amount["\s:]+([^,\n"]+)',
            "tax_rate": r'tax_rate["\s:]+([^,\n"]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip().strip('"').strip()
                if value and value.lower() != 'null':
                    extracted[key] = value
        
        # KDV oranı için özel fallback - eğer JSON'dan çıkarılamadıysa
        if not extracted["tax_rate"]:
            extracted["tax_rate"] = self.extract_kdv_rate_from_text(text)
            
            # Eğer hala bulunamadıysa, KDV tutarı ve toplam tutardan hesapla
            if not extracted["tax_rate"] and extracted["tax_amount"] and extracted["total_amount"]:
                calculated_rate = self.calculate_kdv_rate_from_amounts(
                    extracted["tax_amount"], 
                    extracted["total_amount"]
                )
                if calculated_rate:
                    extracted["tax_rate"] = calculated_rate
        
        return extracted
    
    def extract_kdv_rate_from_text(self, text: str) -> Optional[str]:
        """
        Metinden KDV oranını çıkarmak için gelişmiş regex pattern'leri
        """
        # KDV oranı için çeşitli pattern'ler
        kdv_patterns = [
            # Açık oran yazıları
            r'%(\d{1,2})',  # %18, %20
            r'(\d{1,2})%',  # 18%, 20%
            
            # KDV ile birlikte
            r'KDV\s*[:\-]?\s*%?(\d{1,2})',  # KDV: 18, KDV %18, KDV-18
            r'K\.D\.V\s*[:\-]?\s*%?(\d{1,2})',  # K.D.V: 18
            
            # Sayı + KDV formatı
            r'(\d{1,2})\s+KDV',  # 18 KDV
            r'(\d{1,2})\s+K\.D\.V',  # 18 K.D.V
            
            # Tablo formatları
            r'KDV\s*\(%?(\d{1,2})\)',  # KDV (%18)
            r'(\d{1,2})\s*KDV\s*Oranı',  # 18 KDV Oranı
            
            # Yaygın Türk KDV oranları
            r'\b(0|1|8|18|20)\b(?=.*KDV)',  # 0, 1, 8, 18, 20 (KDV kelimesi yakınında)
        ]
        
        found_rates = []
        
        for pattern in kdv_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                rate = str(match).strip()
                # Geçerli KDV oranı kontrolü (0, 1, 8, 18, 20)
                if rate in ['0', '1', '8', '18', '20']:
                    found_rates.append(int(rate))
        
        if found_rates:
            # En yüksek oranı döndür (genellikle ana KDV oranı)
            return str(max(found_rates))
        
        return None
    
    def calculate_kdv_rate_from_amounts(self, tax_amount: str, total_amount: str) -> Optional[str]:
        """
        KDV tutarı ve toplam tutardan KDV oranını hesaplar
        """
        try:
            # Tutarları temizle ve sayıya çevir
            tax_clean = re.sub(r'[^\d,.]', '', str(tax_amount))
            total_clean = re.sub(r'[^\d,.]', '', str(total_amount))
            
            # Virgülü noktaya çevir
            tax_clean = tax_clean.replace(',', '.')
            total_clean = total_clean.replace(',', '.')
            
            tax_value = float(tax_clean)
            total_value = float(total_clean)
            
            if tax_value > 0 and total_value > 0:
                # KDV oranı = (KDV tutarı / (Toplam tutar - KDV tutarı)) * 100
                net_amount = total_value - tax_value
                if net_amount > 0:
                    calculated_rate = (tax_value / net_amount) * 100
                    
                    # Yaygın KDV oranlarına yuvarla (0, 1, 8, 18, 20)
                    common_rates = [0, 1, 8, 18, 20]
                    closest_rate = min(common_rates, key=lambda x: abs(x - calculated_rate))
                    
                    # Eğer hesaplanan oran yaygın oranlardan birine yakınsa kabul et
                    if abs(closest_rate - calculated_rate) < 1:  # 1% tolerans
                        return str(closest_rate)
            
        except (ValueError, ZeroDivisionError):
            pass
        
        return None
    
    def calculate_extraction_score(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ana 4 alanın (Şirket, Fatura No, KDV, Tutar) çıkarma başarısını skorlar
        """
        score = {
            "company_name": 0,
            "invoice_number": 0,
            "tax_amount": 0,
            "total_amount": 0,
            "tax_rate": 0,
            "overall": 0
        }
        
        # Şirket adı skoru
        if extracted_data.get("company_name"):
            company = str(extracted_data["company_name"]).strip()
            if len(company) >= 3:  # En az 3 karakter
                score["company_name"] = 100
            else:
                score["company_name"] = 50
        
        # Fatura No skoru
        if extracted_data.get("invoice_number"):
            invoice_no = str(extracted_data["invoice_number"]).strip()
            if len(invoice_no) >= 3:  # En az 3 karakter
                score["invoice_number"] = 100
            else:
                score["invoice_number"] = 50
        
        # KDV skoru
        if extracted_data.get("tax_amount"):
            tax = str(extracted_data["tax_amount"]).strip()
            if re.match(r'\d+[.,]\d{2}', tax):  # Doğru format
                score["tax_amount"] = 100
            else:
                score["tax_amount"] = 50
        
        # Tutar skoru
        if extracted_data.get("total_amount"):
            amount = str(extracted_data["total_amount"]).strip()
            if re.match(r'\d+[.,]\d{2}', amount):  # Doğru format
                score["total_amount"] = 100
            else:
                score["total_amount"] = 50
        
        # KDV oranı skoru
        if extracted_data.get("tax_rate"):
            rate = str(extracted_data["tax_rate"]).strip()
            if re.match(r'\d+', rate):  # Sadece sayı
                score["tax_rate"] = 100
            else:
                score["tax_rate"] = 50
        
        # Genel skor (5 ana alan ortalaması)
        score["overall"] = (score["company_name"] + score["invoice_number"] + score["tax_amount"] + score["total_amount"] + score["tax_rate"]) / 5
        
        return score