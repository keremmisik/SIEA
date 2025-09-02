# SMART INVOICE ENTRY AUTOMATION (SIEA)

## 🎯 Proje Açıklaması
SIEA, kullanıcıların kamera ile fatura tarayarak veya fotoğraf çekerek otomatik veri girişi yapabilmelerini sağlayan akıllı bir fatura işleme sistemidir. Modern web teknolojileri ve OCR teknolojisi kullanarak fatura verilerini otomatik olarak çıkarır ve güvenli bir şekilde saklar.

## ✨ Özellikler
- 📷 **Kamera Entegrasyonu:** Web kamerası ile gerçek zamanlı fatura tarama
- 📁 **Dosya Yükleme:** Drag & drop ile fatura fotoğrafı yükleme
- 🤖 **AI OCR:** Google Gemini 1.5 Flash ile akıllı veri çıkarma
- 🗄️ **Güvenli Depolama:** PostgreSQL'de şifreli veri saklama
- 📊 **Excel Export:** Stillendirilmiş Excel dosyası oluşturma (.xlsx)
- 🔒 **Veri Güvenliği:** 5 yıllık otomatik veri silme politikası
- 👤 **Kullanıcı Yönetimi:** JWT tabanlı kimlik doğrulama
- 📱 **Responsive Design:** Mobil ve masaüstü uyumlu arayüz
- 🎨 **Modern UI:** Tailwind CSS ile tasarlanmış kullanıcı dostu arayüz

## 🛠 Teknoloji Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT + bcrypt
- **AI OCR:** Google Gemini 1.5 Flash
- **Excel:** pandas + openpyxl + xlsxwriter
- **Encryption:** cryptography (Fernet)

### Frontend
- **Framework:** React.js 18
- **Routing:** React Router DOM
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Camera:** react-webcam
- **File Upload:** react-dropzone
- **Notifications:** react-toastify
- **HTTP Client:** Axios

### DevOps & Deployment
- **Containerization:** Docker + Docker Compose
- **Web Server:** Nginx
- **SSL:** Let's Encrypt
- **Database Migration:** Custom migration system

## 📱 Sayfa Yapısı
1. **🔐 Giriş/Kayıt:** Kullanıcı kimlik doğrulama
2. **📷 Tarama Sayfası:** Kamera/dosya yükleme ile fatura tarama
3. **📋 İşlem Görmüş Faturalar:** Taranan faturaların listesi, arama ve Excel export
4. **👤 Profil Sayfası:** Kullanıcı hesap bilgileri ve ayarları

## 🚀 Hızlı Kurulum

### Otomatik Kurulum (Önerilen)
```bash
# Projeyi klonlayın
git clone <repository-url>
cd SIEA

# Otomatik kurulum scriptini çalıştırın
python setup.py
```

### Manuel Kurulum

#### Gereksinimler
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Tesseract OCR

#### 1. Backend Kurulumu
```bash
cd backend

# Virtual environment oluştur
python -m venv venv

# Virtual environment'ı aktif et
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment dosyasını oluştur
cp env_example.txt .env
# .env dosyasını düzenleyin

# Veritabanı migration'ını çalıştır
python database/migrations.py

# Sunucuyu başlat
uvicorn main:app --reload
```

#### 2. Frontend Kurulumu
```bash
cd frontend

# Bağımlılıkları yükle
npm install

# Development sunucusunu başlat
npm start
```

#### 3. Veritabanı Kurulumu
```sql
-- PostgreSQL'e bağlanın ve veritabanını oluşturun
CREATE DATABASE siea_db;
CREATE USER siea_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE siea_db TO siea_user;
```

## 🐳 Docker ile Kurulum

### Development Ortamı
```bash
# Development servislerini başlat
docker-compose -f docker-compose.dev.yml up -d

# Backend ve frontend'i manuel başlatın
cd backend && python main.py
cd frontend && npm start
```

### Production Ortamı
```bash
# Production deployment
./scripts/deploy-production.sh your-domain.com admin@your-domain.com
```

## 📖 API Dokümantasyonu
Backend çalıştıktan sonra API dokümantasyonuna erişebilirsiniz:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Ana API Endpoint'leri
- `POST /auth/register` - Kullanıcı kaydı
- `POST /auth/login` - Kullanıcı girişi
- `POST /invoices/upload` - Fatura yükleme ve OCR işlemi
- `GET /invoices` - Kullanıcının faturalarını listele
- `GET /invoices/export/excel` - Excel export
- `GET /user/profile` - Kullanıcı profili

## 🔧 Konfigürasyon

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/siea_db

# Security
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# OCR
TESSERACT_CMD=tesseract  # Windows: C:\Program Files\Tesseract-OCR\tesseract.exe

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf
```

## 🛡 Güvenlik Özellikleri
- **Veri Şifreleme:** Tüm fatura verileri AES-256 ile şifrelenir
- **JWT Authentication:** Güvenli kullanıcı oturumları
- **Password Hashing:** bcrypt ile şifre hashleme
- **SQL Injection Protection:** SQLAlchemy ORM koruması
- **CORS Protection:** Yapılandırılabilir CORS politikaları
- **File Upload Security:** Dosya tipi ve boyut kontrolü
- **Automatic Data Cleanup:** 5 yıllık otomatik veri silme

## 📊 Veri Modeli
```
Users
├── id (Primary Key)
├── email (Unique)
├── full_name
├── hashed_password
└── created_at

Invoices
├── id (Primary Key)
├── user_id (Foreign Key)
├── filename
├── ocr_data (Encrypted JSON)
├── invoice_number
├── company_name
├── total_amount
└── expires_at (5 years)

Audit_Logs
├── id (Primary Key)
├── user_id (Foreign Key)
├── action
├── resource_type
└── created_at
```

## 🔄 OCR İşlemi Detayları
1. **Görüntü Ön İşleme:** Gri tonlama, gürültü azaltma, kontrast artırma
2. **OCR Çıkarma:** Tesseract ile Türkçe/İngilizce metin tanıma
3. **Veri Parsing:** Regex ile fatura bilgilerini çıkarma:
   - Fatura numarası
   - Şirket adı
   - Tarih bilgisi
   - Toplam tutar
   - KDV tutarı
4. **Doğrulama:** Çıkarılan verilerin tutarlılık kontrolü

## 📈 Performans Optimizasyonları
- **Database Indexing:** Kritik alanlarda indeks kullanımı
- **Image Processing:** Optimize edilmiş görüntü işleme
- **Caching:** Redis ile oturum cache'leme
- **Lazy Loading:** Frontend'de bileşen lazy loading
- **Code Splitting:** React bundle optimizasyonu

## 🧪 Test Etme
```bash
# Backend testleri
cd backend
pytest

# Frontend testleri
cd frontend
npm test

# Integration testleri
npm run test:integration
```

## 📦 Deployment Seçenekleri

### 1. Traditional Server
- Nginx + Gunicorn/Uvicorn
- PostgreSQL
- SSL sertifikası (Let's Encrypt)

### 2. Docker Container
- Docker Compose ile multi-container setup
- Otomatik SSL yenileme
- Health check'ler

### 3. Cloud Platforms
- **Heroku:** Kolay deployment
- **AWS:** EC2 + RDS + S3
- **DigitalOcean:** Droplet + Managed Database
- **Google Cloud:** Compute Engine + Cloud SQL

## 🔍 Troubleshooting

### Yaygın Sorunlar ve Çözümleri

#### OCR Çalışmıyor
```bash
# Tesseract kurulumu kontrol et
tesseract --version

# Türkçe dil paketi yükle
sudo apt-get install tesseract-ocr-tur  # Linux
```

#### Database Connection Error
```bash
# PostgreSQL servisini kontrol et
sudo systemctl status postgresql

# Connection string'i kontrol et
psql -d "postgresql://username:password@localhost:5432/siea_db"
```

#### Frontend Build Hatası
```bash
# Node modules'ü temizle
rm -rf node_modules package-lock.json
npm install
```

## 📋 Roadmap
- [ ] **v1.1:** Çoklu dil desteği
- [ ] **v1.2:** Mobil uygulama (React Native)
- [ ] **v1.3:** AI tabanlı fatura kategorilendirme
- [ ] **v1.4:** API entegrasyonları (SAP, Logo vs.)
- [ ] **v1.5:** Gerçek zamanlı dashboard
- [ ] **v2.0:** Microservices mimarisi

## 🤝 Katkıda Bulunma
1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans
Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.

## 📞 Destek
- **Issues:** GitHub Issues kullanın
- **Documentation:** Wiki sayfalarını kontrol edin
- **Email:** support@siea.local (geliştirme amaçlı)

## 🙏 Teşekkürler
- **Tesseract OCR:** Google tarafından geliştirilen OCR motoru
- **OpenCV:** Bilgisayar görme kütüphanesi
- **FastAPI:** Modern Python web framework
- **React:** Facebook tarafından geliştirilen UI kütüphanesi

---

**SIEA** - Smart Invoice Entry Automation 🚀
