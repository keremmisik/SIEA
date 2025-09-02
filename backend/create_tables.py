"""
Basit tablo oluşturma scripti
"""

import os
from sqlalchemy import create_engine
from decouple import config

# Database models
from database.models import Base

def main():
    # Database URL'i al
    DATABASE_URL = config('DATABASE_URL', default='postgresql://postgres:password@localhost:5432/siea_db')
    
    print(f"🔗 Veritabanına bağlanılıyor: {DATABASE_URL.replace('password', '***')}")
    
    try:
        # Engine oluştur
        engine = create_engine(DATABASE_URL)
        
        # Tüm tabloları oluştur
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tüm tablolar başarıyla oluşturuldu!")
        print("📋 Oluşturulan tablolar:")
        for table in Base.metadata.tables.keys():
            print(f"   - {table}")
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
