# GitHub Repository Setup Guide

## 📋 Adım Adım GitHub Repo Oluşturma

### 1. GitHub'da Yeni Repo Oluştur

1. [GitHub](https://github.com) sitesine git
2. Sağ üst köşedeki **"+"** butonuna tıkla
3. **"New repository"** seç
4. **Repository name:** `SIEA` veya `smart-invoice-automation`
5. **Description:** `Smart Invoice Entry Automation - AI-powered invoice processing system`
6. **Public** veya **Private** seç
7. **Initialize with README** seçmeyin (zaten var)
8. **Create repository** butonuna tıkla

### 2. Local Git Repository Başlat

Terminal/PowerShell'de proje dizininde:

```bash
# Git repository başlat
git init

# Tüm dosyaları staging area'ya ekle
git add .

# İlk commit
git commit -m "Initial commit: SIEA - Smart Invoice Entry Automation"

# GitHub repo'yu remote olarak ekle (YOUR_USERNAME değiştir)
git remote add origin https://github.com/YOUR_USERNAME/SIEA.git

# Main branch'e push et
git branch -M main
git push -u origin main
```

### 3. Environment Variables Ayarla

⚠️ **ÖNEMLİ:** `.env` dosyası GitHub'a push edilmeyecek (.gitignore'da)

1. `backend/env_example.txt` dosyasını kopyala
2. `.env` adıyla yeniden adlandır
3. API key'lerini ve şifrelerini güncelle:

```bash
# Secret key oluştur
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Encryption key oluştur
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 4. GitHub Repository Features

#### Branch Protection Rules
- Settings → Branches → Add rule
- Branch name pattern: `main`
- Require pull request reviews

#### GitHub Actions (İsteğe bağlı)
- `.github/workflows/` klasörü oluştur
- CI/CD pipeline'ları ekle

#### Issues ve Projects
- Issues sekmesini etkinleştir
- Project board oluştur

### 5. Colaborators Ekle

- Settings → Manage access
- **Invite a collaborator** ile ekip üyelerini davet et

### 6. Repository Settings

#### About Section
- Repository ana sayfasında **⚙️** → **Edit**
- Website: Canlı demo URL'si
- Topics: `fastapi`, `react`, `ocr`, `invoice`, `automation`, `gemini-ai`

#### Social Preview
- Proje için bir banner/logo ekle

## 🔧 Geliştirme Workflow'u

### Feature Branch Workflow
```bash
# Yeni feature branch oluştur
git checkout -b feature/yeni-ozellik

# Değişiklikleri commit et
git add .
git commit -m "feat: yeni özellik eklendi"

# GitHub'a push et
git push origin feature/yeni-ozellik

# Pull Request oluştur
```

### Commit Message Conventions
- `feat:` - Yeni özellik
- `fix:` - Bug düzeltme
- `docs:` - Dokümantasyon
- `style:` - Kod formatı
- `refactor:` - Kod refactoring
- `test:` - Test ekleme

## 🚀 Deployment

### GitHub Pages (Frontend)
- Settings → Pages
- Source: GitHub Actions
- React build dosyalarını deploy et

### Heroku/Railway (Backend)
- Environment variables'ı platform'da ayarla
- PostgreSQL addon ekle
- Auto-deploy branch: `main`

## 📊 Repository İstatistikleri

Repo oluşturduktan sonra:
- ⭐ Star sayısını takip et
- 👀 Watch'ları gözlemle
- 🍴 Fork'ları kontrol et
- 📈 Traffic analytics'i incele

## 🔒 Güvenlik

- Secrets'ları GitHub Secrets'ta sakla
- Dependabot'u etkinleştir
- Security advisories'i takip et
- Code scanning'i aç
