from PIL import Image
import io
import re
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
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
    "tax_rate": "kdv_oranı",
    "has_multiple_products": true/false,
    "products": [
        {
            "product_name": "ürün_adı",
            "quantity": "miktar",
            "unit_price": "birim_fiyat",
            "total_price": "toplam_fiyat",
            "tax_rate": "kdv_oranı",
            "tax_amount": "kdv_tutarı"
        }
    ]
}

KURALLAR:
1. ŞİRKET ADI: Faturanın EN ÜST satırında bulunan şirket ismi
2. FATURA NO: Fatura numarasını bulmak için şu öncelik sırasını takip et:
   - ÖNCE: "FATURA NO:", "FATURA NUMARASI:", "FATURA NO" yazısının yanındaki değer
   - EĞER FATURA NO YOKSA: "BELGE NO:", "BELGE NUMARASI:", "BELGE NO" yazısının yanındaki değer
   - EĞER İKİSİ DE YOKSA: "NO:", "NUMARA:", "SIRA NO" yazısının yanındaki değer
   - Değer harf+sayı olabilir (örn: F2024001, 2024-001, ABC123)
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

ÇOKLU ÜRÜN DETAYLARI:
- has_multiple_products: Eğer faturada birden fazla farklı ürün varsa true, tek ürün varsa false
- products: Her ürün için ayrı obje oluştur
- Her ürün için kendi KDV oranını ve tutarını belirle
- Eğer tek ürün varsa, products array'ini boş bırak (eski sistem gibi çalışsın)
- Eğer birden fazla ürün varsa, her ürün için:
  - product_name: Ürün adı veya açıklaması
  - quantity: Miktar (adet, kg, vs.) - eğer bulunamazsa "1" yaz (MUTLAKA STRING OLARAK)
  - unit_price: Birim fiyat (çok dikkatli analiz et) (MUTLAKA STRING OLARAK)
  - total_price: O ürünün toplam fiyatı (MUTLAKA STRING OLARAK)
  - tax_rate: O ürünün KDV oranı (sadece sayı) (MUTLAKA STRING OLARAK)
  - tax_amount: O ürünün KDV tutarı (MUTLAKA STRING OLARAK)

BİRİM FİYAT ANALİZİ İÇİN ÖNEMLİ KURALLAR:
- Birim fiyat genellikle "adet", "kg", "lt", "m²" gibi birimlerle birlikte yazılır
- "Birim Fiyat", "Fiyat", "Adet Fiyat" gibi başlıkların altındaki değerleri bul
- Tablolarda genellikle 2. veya 3. sütunda yer alır
- Virgülle ayrılmış ondalık sayılar olabilir (örn: 15,50)
- Nokta ile ayrılmış binlik ayırıcı olabilir (örn: 1.250,75)
- Eğer birim fiyat bulunamazsa ama toplam fiyat ve miktar varsa hesapla: total_price / quantity
- Para birimi sembolleri (TL, ₺) kullanma, sadece sayıyı döndür

ÖNEMLİ KDV ORANI DETAYLARI:
- Eğer birden fazla KDV oranı varsa, TÜM KDV oranlarını topla (örn: %1 + %10 = %11)
- Farklı ürünlerde farklı KDV oranları olabilir, bunları toplam KDV oranı olarak hesapla
- Eğer KDV oranı bulunamazsa ama KDV tutarı varsa, hesapla: (KDV tutarı / (toplam tutar - KDV tutarı)) * 100
- KDV oranı genellikle 0, 1, 8, 18 veya 20 olur
- Tablolarda, sütun başlıklarında veya satır sonlarında olabilir
- Örnek: Faturada %1 KDV'li ürünler ve %10 KDV'li ürünler varsa, toplam KDV oranı %11 olur

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
                
                # Fatura numarası için öncelik kontrolü
                if not extracted_data.get("invoice_number"):
                    extracted_data["invoice_number"] = self.extract_invoice_number_with_priority(response.text)
                
                # KDV oranı için ek kontrol - JSON'da null ise fallback kullan
                if not extracted_data.get("tax_rate"):
                    # Önce genel KDV oranı tespit et
                    extracted_data["tax_rate"] = self.extract_kdv_rate_from_text(response.text)
                    
                    # Eğer bulunamadıysa, ürün bazında KDV oranlarını tespit et
                    if not extracted_data["tax_rate"]:
                        extracted_data["tax_rate"] = self.extract_product_based_kdv_rates(response.text)
                    
                    # Eğer hala bulunamadıysa, KDV tutarı ve toplam tutardan hesapla
                    if not extracted_data["tax_rate"] and extracted_data.get("tax_amount") and extracted_data.get("total_amount"):
                        calculated_rate = self.calculate_kdv_rate_from_amounts(
                            extracted_data["tax_amount"], 
                            extracted_data["total_amount"]
                        )
                        if calculated_rate:
                            extracted_data["tax_rate"] = calculated_rate
                
                # Çoklu ürün verilerini işle ve birim fiyatları hesapla
                if extracted_data.get("has_multiple_products") and extracted_data.get("products"):
                    try:
                        extracted_data["products"] = self.process_products_data(extracted_data["products"])
                    except Exception as e:
                        print(f"❌ Ürün verileri işlenirken hata: {e}")
                        # Hata durumunda products array'ini boş bırak
                        extracted_data["products"] = []
                            
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
            "tax_rate": None,
            "has_multiple_products": False,
            "products": []
        }
        
        # Basit regex'lerle çıkar
        patterns = {
            "company_name": r'company_name["\s:]+([^,\n"]+)',
            "invoice_date": r'invoice_date["\s:]+([^,\n"]+)',
            "total_amount": r'total_amount["\s:]+([^,\n"]+)',
            "tax_amount": r'tax_amount["\s:]+([^,\n"]+)',
            "tax_rate": r'tax_rate["\s:]+([^,\n"]+)'
        }
        
        # Fatura numarası için öncelik sırası
        invoice_number_patterns = [
            r'invoice_number["\s:]+([^,\n"]+)',  # JSON'dan gelen
            r'FATURA\s+NO[:\s]+([A-Za-z0-9\-_/]+)',  # FATURA NO: pattern
            r'FATURA\s+NUMARASI[:\s]+([A-Za-z0-9\-_/]+)',  # FATURA NUMARASI: pattern
            r'BELGE\s+NO[:\s]+([A-Za-z0-9\-_/]+)',  # BELGE NO: pattern
            r'BELGE\s+NUMARASI[:\s]+([A-Za-z0-9\-_/]+)',  # BELGE NUMARASI: pattern
            r'NO[:\s]+([A-Za-z0-9\-_/]+)',  # NO: pattern
            r'NUMARA[:\s]+([A-Za-z0-9\-_/]+)',  # NUMARA: pattern
        ]
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip().strip('"').strip()
                if value and value.lower() != 'null':
                    extracted[key] = value
        
        # Fatura numarası için öncelik sırası ile arama
        for pattern in invoice_number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip().strip('"').strip()
                if value and value.lower() != 'null' and len(value) > 0:
                    extracted["invoice_number"] = value
                    print(f"🔍 Fatura numarası bulundu: {value} (Pattern: {pattern})")
                    break  # İlk bulunan değeri kullan (öncelik sırası)
        
        # KDV oranı için özel fallback - eğer JSON'dan çıkarılamadıysa
        if not extracted["tax_rate"]:
            # Önce genel KDV oranı tespit et
            extracted["tax_rate"] = self.extract_kdv_rate_from_text(text)
            
            # Eğer bulunamadıysa, ürün bazında KDV oranlarını tespit et
            if not extracted["tax_rate"]:
                extracted["tax_rate"] = self.extract_product_based_kdv_rates(text)
            
            # Eğer hala bulunamadıysa, KDV tutarı ve toplam tutardan hesapla
            if not extracted["tax_rate"] and extracted["tax_amount"] and extracted["total_amount"]:
                calculated_rate = self.calculate_kdv_rate_from_amounts(
                    extracted["tax_amount"], 
                    extracted["total_amount"]
                )
                if calculated_rate:
                    extracted["tax_rate"] = calculated_rate
        
        # Çoklu ürün verilerini işle ve string garantisi ver
        if extracted.get("has_multiple_products") and extracted.get("products"):
            try:
                extracted["products"] = self.process_products_data(extracted["products"])
            except Exception as e:
                print(f"❌ Fallback ürün verileri işlenirken hata: {e}")
                extracted["products"] = []
        
        return extracted
    
    def extract_kdv_rate_from_text(self, text: str) -> Optional[str]:
        """
        Metinden KDV oranını çıkarmak için gelişmiş regex pattern'leri
        Birden fazla ürün olduğunda tüm KDV oranlarını toplar
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
            # Benzersiz KDV oranlarını topla (aynı oranı birden fazla kez saymamak için)
            unique_rates = list(set(found_rates))
            total_rate = sum(unique_rates)
            print(f"🔍 Bulunan KDV oranları: {unique_rates}, Toplam: {total_rate}%")
            return str(total_rate)
        
        return None
    
    def extract_product_based_kdv_rates(self, text: str) -> Optional[str]:
        """
        Faturada ürün bazında KDV oranlarını tespit eder ve toplar
        """
        # Ürün satırlarını tespit etmek için pattern'ler
        product_patterns = [
            # Tablo formatında ürün satırları
            r'(\d+[.,]\d{2})\s*TL.*?(\d{1,2})%',  # Tutar TL ... %18
            r'(\d{1,2})%.*?(\d+[.,]\d{2})\s*TL',  # %18 ... Tutar TL
            r'KDV\s*(\d{1,2})%.*?(\d+[.,]\d{2})',  # KDV 18% ... Tutar
            r'(\d+[.,]\d{2}).*?KDV\s*(\d{1,2})%',  # Tutar ... KDV 18%
        ]
        
        found_rates = []
        
        for pattern in product_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Match'ten KDV oranını çıkar
                for group in match:
                    if group.isdigit() and int(group) in [0, 1, 8, 18, 20]:
                        found_rates.append(int(group))
        
        if found_rates:
            # Benzersiz oranları topla
            unique_rates = list(set(found_rates))
            total_rate = sum(unique_rates)
            print(f"🛍️ Ürün bazında bulunan KDV oranları: {unique_rates}, Toplam: {total_rate}%")
            return str(total_rate)
        
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
    
    def extract_invoice_number_with_priority(self, text: str) -> Optional[str]:
        """
        Fatura numarasını öncelik sırası ile çıkarır: Fatura No > Belge No > No
        """
        # Fatura numarası için öncelik sırası
        invoice_number_patterns = [
            r'FATURA\s+NO[:\s]+([A-Za-z0-9\-_/]+)',  # FATURA NO: pattern
            r'FATURA\s+NUMARASI[:\s]+([A-Za-z0-9\-_/]+)',  # FATURA NUMARASI: pattern
            r'BELGE\s+NO[:\s]+([A-Za-z0-9\-_/]+)',  # BELGE NO: pattern
            r'BELGE\s+NUMARASI[:\s]+([A-Za-z0-9\-_/]+)',  # BELGE NUMARASI: pattern
            r'NO[:\s]+([A-Za-z0-9\-_/]+)',  # NO: pattern
            r'NUMARA[:\s]+([A-Za-z0-9\-_/]+)',  # NUMARA: pattern
        ]
        
        for i, pattern in enumerate(invoice_number_patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip().strip('"').strip()
                if value and value.lower() != 'null' and len(value) > 0:
                    priority_type = ["FATURA NO", "FATURA NUMARASI", "BELGE NO", "BELGE NUMARASI", "NO", "NUMARA"][i]
                    print(f"🔍 Fatura numarası bulundu: {value} (Öncelik: {priority_type})")
                    return value
        
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
    
    def process_products_data(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ürün verilerini işler ve eksik birim fiyatları hesaplar
        """
        if not products or not isinstance(products, list):
            print("⚠️ Geçersiz ürün verisi")
            return []
        
        processed_products = []
        
        for i, product in enumerate(products):
            try:
                if not isinstance(product, dict):
                    print(f"⚠️ Ürün {i} geçersiz format: {product}")
                    continue
                    
                processed_product = product.copy()
                
                # Miktar için default değer - string olarak garantile
                if not processed_product.get("quantity"):
                    processed_product["quantity"] = "1"
                else:
                    # Eğer integer ise string'e çevir
                    if isinstance(processed_product["quantity"], (int, float)):
                        processed_product["quantity"] = str(int(processed_product["quantity"]))
                
                # Tax rate için string garantisi
                if processed_product.get("tax_rate"):
                    if isinstance(processed_product["tax_rate"], (int, float)):
                        processed_product["tax_rate"] = str(int(processed_product["tax_rate"]))
                
                # Birim fiyat hesaplama
                if not processed_product.get("unit_price") and processed_product.get("total_price") and processed_product.get("quantity"):
                    try:
                        total_price = self.clean_amount(processed_product["total_price"])
                        quantity = self.clean_amount(processed_product["quantity"])
                        
                        if total_price and quantity and quantity > 0:
                            unit_price = total_price / quantity
                            processed_product["unit_price"] = f"{unit_price:.2f}".replace('.', ',')
                            print(f"🔢 Birim fiyat hesaplandı: {processed_product['unit_price']} TL")
                    except (ValueError, ZeroDivisionError) as e:
                        print(f"⚠️ Birim fiyat hesaplama hatası: {e}")
                
                processed_products.append(processed_product)
                
            except Exception as e:
                print(f"❌ Ürün {i} işlenirken hata: {e}")
                # Hatalı ürünü atla ama devam et
                continue
        
        return processed_products
    
    def clean_amount(self, amount_str: str) -> Optional[float]:
        """
        Tutar string'ini temizler ve float'a çevirir
        """
        if not amount_str:
            return None
        
        try:
            # Virgülü noktaya çevir ve sayı olmayan karakterleri temizle
            cleaned = re.sub(r'[^\d,.]', '', str(amount_str))
            cleaned = cleaned.replace(',', '.')
            
            # Eğer sadece nokta varsa (binlik ayırıcı), onu kaldır
            if '.' in cleaned and ',' not in cleaned:
                # Son 3 karakterden önce nokta varsa binlik ayırıcıdır
                parts = cleaned.split('.')
                if len(parts) == 2 and len(parts[1]) == 3:
                    cleaned = cleaned.replace('.', '')
                else:
                    # Ondalık ayırıcı olarak kabul et
                    pass
            
            return float(cleaned)
        except (ValueError, TypeError):
            return None