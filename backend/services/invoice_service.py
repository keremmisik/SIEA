from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database.models import Invoice
from schemas.invoice_schemas import InvoiceCreate
from services.encryption_service import EncryptionService

class InvoiceService:
    def __init__(self):
        self.encryption_service = EncryptionService()
    
    def create_invoice(self, invoice_data: InvoiceCreate, db: Session) -> Invoice:
        """Yeni fatura kaydı oluştur"""
        
        # OCR verilerini şifrele
        encrypted_ocr_data = self.encryption_service.encrypt_data(invoice_data.ocr_data)
        
        # OCR'dan çıkarılan verileri parse et
        extracted_data = invoice_data.ocr_data.get('extracted_data', {})
        
        # Tarihi parse et
        invoice_date = None
        if extracted_data.get('invoice_date'):
            try:
                # Farklı tarih formatlarını dene
                date_str = extracted_data['invoice_date']
                for fmt in ['%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        invoice_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
            except:
                pass
        
        # Veritabanı modeli oluştur
        db_invoice = Invoice(
            filename=invoice_data.filename,
            ocr_data=encrypted_ocr_data,
            user_id=invoice_data.user_id,
            invoice_number=extracted_data.get('invoice_number'),
            invoice_date=invoice_date,
            company_name=extracted_data.get('company_name'),
            total_amount=extracted_data.get('total_amount'),
            tax_amount=extracted_data.get('tax_amount'),
            tax_rate=extracted_data.get('tax_rate')
        )
        
        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)
        
        # OCR verisini decrypt ederek döndür
        if db_invoice.ocr_data:
            try:
                db_invoice.ocr_data = self.encryption_service.decrypt_data(db_invoice.ocr_data)
            except:
                db_invoice.ocr_data = {}
        
        return db_invoice
    
    def get_user_invoices(self, user_id: int, db: Session) -> List[Invoice]:
        """Kullanıcının tüm faturalarını getir"""
        invoices = db.query(Invoice).filter(
            Invoice.user_id == user_id
        ).order_by(Invoice.created_at.desc()).all()
        
        # OCR verilerini decrypt et
        for invoice in invoices:
            if invoice.ocr_data:
                try:
                    invoice.ocr_data = self.encryption_service.decrypt_data(invoice.ocr_data)
                except:
                    # Decrypt hatası durumunda boş dict döndür
                    invoice.ocr_data = {}
        
        return invoices
    
    def get_invoice(self, invoice_id: int, user_id: int, db: Session) -> Optional[Invoice]:
        """Belirli bir faturayı getir"""
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.user_id == user_id
        ).first()
        
        if invoice and invoice.ocr_data:
            try:
                invoice.ocr_data = self.encryption_service.decrypt_data(invoice.ocr_data)
            except:
                invoice.ocr_data = {}
        
        return invoice
    
    def delete_expired_invoices(self, db: Session) -> int:
        """Süresi dolmuş faturaları sil (5 yıl)"""
        current_time = datetime.utcnow()
        
        expired_invoices = db.query(Invoice).filter(
            Invoice.expires_at <= current_time
        ).all()
        
        count = len(expired_invoices)
        
        for invoice in expired_invoices:
            db.delete(invoice)
        
        db.commit()
        
        return count
    
    def get_invoice_statistics(self, user_id: int, db: Session) -> dict:
        """Kullanıcının fatura istatistiklerini getir"""
        total_invoices = db.query(Invoice).filter(Invoice.user_id == user_id).count()
        
        # Bu ay işlenen faturalar
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_invoices = db.query(Invoice).filter(
            Invoice.user_id == user_id,
            Invoice.created_at >= current_month_start
        ).count()
        
        return {
            "total_invoices": total_invoices,
            "monthly_invoices": monthly_invoices,
            "last_processed": db.query(Invoice).filter(
                Invoice.user_id == user_id
            ).order_by(Invoice.created_at.desc()).first()
        }
