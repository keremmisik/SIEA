"""
Database migration script for SIEA
Bu script veritabanı tablolarını oluşturur ve gerekli indeksleri ekler.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.database import DATABASE_URL, Base
from database.models import User, Invoice, AuditLog
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Tüm tabloları oluştur"""
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tüm tablolar başarıyla oluşturuldu")
        
        # İndeksleri ekle
        create_indexes(engine)
        
    except Exception as e:
        logger.error(f"❌ Tablo oluşturma hatası: {e}")
        raise

def create_indexes(engine):
    """Performans için indeksler ekle"""
    try:
        with engine.connect() as conn:
            # Users tablosu indeksleri
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)"))
            
            # Invoices tablosu indeksleri
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON invoices(created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_invoices_expires_at ON invoices(expires_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_invoices_invoice_date ON invoices(invoice_date)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_invoices_company ON invoices(company_name)"))
            
            # Audit logs indeksleri
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)"))
            
            conn.commit()
            logger.info("✅ İndeksler başarıyla oluşturuldu")
            
    except Exception as e:
        logger.error(f"❌ İndeks oluşturma hatası: {e}")
        raise

def create_cleanup_function():
    """Otomatik veri silme fonksiyonu oluştur"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # PostgreSQL fonksiyonu oluştur
            cleanup_function = """
            CREATE OR REPLACE FUNCTION cleanup_expired_invoices()
            RETURNS INTEGER AS $$
            DECLARE
                deleted_count INTEGER;
            BEGIN
                DELETE FROM invoices WHERE expires_at <= NOW();
                GET DIAGNOSTICS deleted_count = ROW_COUNT;
                
                INSERT INTO audit_logs (user_id, action, resource_type, details, created_at)
                VALUES (NULL, 'CLEANUP', 'INVOICE', 
                       json_build_object('deleted_count', deleted_count), NOW());
                
                RETURN deleted_count;
            END;
            $$ LANGUAGE plpgsql;
            """
            
            conn.execute(text(cleanup_function))
            conn.commit()
            logger.info("✅ Cleanup fonksiyonu oluşturuldu")
            
    except Exception as e:
        logger.error(f"❌ Cleanup fonksiyonu oluşturma hatası: {e}")
        raise

def setup_cron_job():
    """Otomatik cleanup için cron job kurulum talimatları"""
    logger.info("""
    📋 CRON JOB KURULUM TALİMATI:
    
    Otomatik veri silme için aşağıdaki cron job'u ekleyin:
    
    # Her gün saat 02:00'da expired faturaları sil
    0 2 * * * psql -d siea_db -c "SELECT cleanup_expired_invoices();"
    
    Kurulum için:
    1. crontab -e
    2. Yukarıdaki satırı ekleyin
    3. Kaydedin ve çıkın
    """)

if __name__ == "__main__":
    logger.info("🚀 SIEA Veritabanı Migration Başlatılıyor...")
    
    create_tables()
    create_cleanup_function()
    setup_cron_job()
    
    logger.info("✅ Migration tamamlandı!")
