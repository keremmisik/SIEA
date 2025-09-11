from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship with invoices
    invoices = relationship("Invoice", back_populates="user")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_image_path = Column(String)  # Encrypted file path
    ocr_data = Column(JSON)  # Extracted invoice data (encrypted)
    processed_at = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Invoice fields extracted by OCR
    invoice_number = Column(String)
    invoice_date = Column(DateTime)
    company_name = Column(String)
    total_amount = Column(String)
    tax_amount = Column(String)
    tax_rate = Column(String)
    
    # Multiple products support
    has_multiple_products = Column(Boolean, default=False)
    products_data = Column(JSON)  # Array of product objects with individual KDV rates
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=5*365))  # 5 years
    
    # Relationship with user
    user = relationship("User", back_populates="invoices")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)  # CREATE, READ, UPDATE, DELETE, EXPORT
    resource_type = Column(String, nullable=False)  # INVOICE, USER
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    # Relationship with user
    user = relationship("User")
