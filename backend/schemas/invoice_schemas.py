from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class InvoiceBase(BaseModel):
    filename: str

class InvoiceCreate(InvoiceBase):
    ocr_data: Dict[str, Any]
    user_id: int

class InvoiceResponse(InvoiceBase):
    id: int
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    company_name: Optional[str] = None
    total_amount: Optional[str] = None
    tax_amount: Optional[str] = None
    tax_rate: Optional[str] = None
    processed_at: datetime
    created_at: datetime
    ocr_data: Optional[Dict[str, Any]] = None
    
    model_config = {"from_attributes": True}

class InvoiceStats(BaseModel):
    total_invoices: int
    monthly_invoices: int
    last_processed: Optional[datetime] = None
