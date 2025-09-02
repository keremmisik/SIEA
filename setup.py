#!/usr/bin/env python3
"""
SIEA - Smart Invoice Entry Automation
Setup Script

Bu script projeyi kurmanız için gerekli tüm adımları otomatik olarak yapar.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Komut çalıştır ve sonucu kontrol et"""
    try:
        print(f"🔄 Çalıştırılıyor: {command}")
        result = subprocess.run(command, shell=shell, cwd=cwd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Hata: {result.stderr}")
            return False
        else:
            print(f"✅ Başarılı: {command}")
            if result.stdout:
                print(result.stdout)
            return True
    except Exception as e:
        print(f"❌ Komut çalıştırma hatası: {e}")
        return False

def check_python_version():
    """Python versiyonunu kontrol et"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 veya üzeri gerekli!")
        print(f"   Mevcut versiyon: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python versiyonu uygun: {version.major}.{version.minor}")
    return True

def check_node_version():
    """Node.js versiyonunu kontrol et"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js bulundu: {version}")
            return True
        else:
            print("❌ Node.js bulunamadı!")
            return False
    except FileNotFoundError:
        print("❌ Node.js kurulu değil!")
        return False

def check_postgresql():
    """PostgreSQL kurulumunu kontrol et"""
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ PostgreSQL bulundu: {version}")
            return True
        else:
            print("❌ PostgreSQL bulunamadı!")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL kurulu değil!")
        return False

def setup_backend():
    """Backend kurulumu"""
    print("\n📦 Backend kurulumu başlatılıyor...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend klasörü bulunamadı!")
        return False
    
    # Virtual environment oluştur
    if not run_command("python -m venv venv", cwd=backend_dir):
        return False
    
    # Activation script path
    if platform.system() == "Windows":
        activate_script = backend_dir / "venv" / "Scripts" / "activate"
        pip_path = backend_dir / "venv" / "Scripts" / "pip"
    else:
        activate_script = backend_dir / "venv" / "bin" / "activate"
        pip_path = backend_dir / "venv" / "bin" / "pip"
    
    # Requirements yükle
    if not run_command(f"{pip_path} install -r requirements.txt", cwd=backend_dir):
        return False
    
    print("✅ Backend kurulumu tamamlandı!")
    return True

def setup_frontend():
    """Frontend kurulumu"""
    print("\n🎨 Frontend kurulumu başlatılıyor...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend klasörü bulunamadı!")
        return False
    
    # NPM dependencies yükle
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    print("✅ Frontend kurulumu tamamlandı!")
    return True

def setup_database():
    """Veritabanı kurulumu"""
    print("\n🗄️ Veritabanı kurulumu başlatılıyor...")
    
    # Veritabanı oluştur
    print("📋 Veritabanı oluşturma talimatları:")
    print("1. PostgreSQL'e bağlanın: psql -U postgres")
    print("2. Veritabanını oluşturun: CREATE DATABASE siea_db;")
    print("3. Kullanıcı oluşturun (opsiyonel): CREATE USER siea_user WITH PASSWORD 'your_password';")
    print("4. Yetkileri verin: GRANT ALL PRIVILEGES ON DATABASE siea_db TO siea_user;")
    
    # Migration çalıştır
    backend_dir = Path("backend")
    if platform.system() == "Windows":
        python_path = backend_dir / "venv" / "Scripts" / "python"
    else:
        python_path = backend_dir / "venv" / "bin" / "python"
    
    print("\n🔄 Migration çalıştırılıyor...")
    if not run_command(f"{python_path} database/migrations.py", cwd=backend_dir):
        print("⚠️ Migration hatası - .env dosyasını kontrol edin")
        return False
    
    print("✅ Veritabanı kurulumu tamamlandı!")
    return True

def create_env_files():
    """Environment dosyalarını oluştur"""
    print("\n⚙️ Environment dosyaları oluşturuluyor...")
    
    # Backend .env
    backend_env = Path("backend") / ".env"
    if not backend_env.exists():
        with open(backend_env, 'w', encoding='utf-8') as f:
            f.write("""# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/siea_db

# Security
SECRET_KEY=your-very-secure-secret-key-change-this-in-production
ENCRYPTION_KEY=your-encryption-key-here

# OCR Configuration
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf

# Data Retention
DATA_RETENTION_YEARS=5
""")
        print("✅ Backend .env dosyası oluşturuldu")
    else:
        print("⚠️ Backend .env dosyası zaten mevcut")
    
    return True

def print_final_instructions():
    """Son talimatları yazdır"""
    print("\n" + "="*60)
    print("🎉 SIEA KURULUM TAMAMLANDI!")
    print("="*60)
    
    print("\n📋 BAŞLATMA TALİMATLARI:")
    print("\n1. Backend başlatma:")
    if platform.system() == "Windows":
        print("   cd backend")
        print("   venv\\Scripts\\activate")
        print("   python main.py")
    else:
        print("   cd backend")
        print("   source venv/bin/activate")
        print("   python main.py")
    
    print("\n2. Frontend başlatma (yeni terminal):")
    print("   cd frontend")
    print("   npm start")
    
    print("\n3. Uygulama URL'leri:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    print("\n⚠️ ÖNEMLİ NOTLAR:")
    print("- backend/.env dosyasındaki veritabanı bilgilerini kontrol edin")
    print("- Tesseract OCR kurulumunu tamamlayın")
    print("- PostgreSQL servisinin çalıştığından emin olun")
    
    print("\n📚 Daha fazla bilgi için README.md dosyasını okuyun.")

def main():
    """Ana kurulum fonksiyonu"""
    print("🚀 SIEA - Smart Invoice Entry Automation Kurulumu")
    print("="*60)
    
    # Sistem gereksinimlerini kontrol et
    print("\n🔍 Sistem gereksinimleri kontrol ediliyor...")
    
    if not check_python_version():
        return False
    
    if not check_node_version():
        print("⚠️ Node.js kurulumu gerekli: https://nodejs.org/")
        return False
    
    if not check_postgresql():
        print("⚠️ PostgreSQL kurulumu gerekli: https://www.postgresql.org/")
        return False
    
    # Environment dosyalarını oluştur
    if not create_env_files():
        return False
    
    # Backend kurulumu
    if not setup_backend():
        return False
    
    # Frontend kurulumu
    if not setup_frontend():
        return False
    
    # Veritabanı kurulumu
    if not setup_database():
        print("⚠️ Veritabanı kurulumu tamamlanamadı - manuel kurulum gerekebilir")
    
    # Final talimatlar
    print_final_instructions()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            print("\n❌ Kurulum başarısız!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Kurulum iptal edildi!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        sys.exit(1)
