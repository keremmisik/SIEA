from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
import os
from datetime import datetime, timedelta
import io
import pandas as pd
from typing import List, Optional

from database.database import get_db, engine
from database import models
from services.ocr_service import OCRService
from services.auth_service import AuthService
from services.invoice_service import InvoiceService
from services.excel_service import ExcelService
from schemas.invoice_schemas import InvoiceResponse, InvoiceCreate
from schemas.user_schemas import UserResponse, UserCreate, UserLogin

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SIEA - Smart Invoice Entry Automation",
    description="Akıllı Fatura Girişi Otomasyon Sistemi",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://10.143.134.27:3000",
        "http://192.168.1.126:3000",
        "http://192.168.56.1:3000",
        "http://172.23.16.1:3000",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Services
ocr_service = OCRService()
auth_service = AuthService()
invoice_service = InvoiceService()
excel_service = ExcelService()

# Auth dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = auth_service.verify_token(credentials.credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return user

@app.get("/")
async def root():
    return {"message": "SIEA - Smart Invoice Entry Automation API"}

# Auth endpoints
@app.post("/auth/register", response_model=dict)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = auth_service.create_user(user_data, db)
        return {"message": "User created successfully", "user_id": user.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", response_model=dict)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        token = auth_service.authenticate_user(user_data, db)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# Invoice endpoints
@app.post("/invoices/upload", response_model=InvoiceResponse)
async def upload_invoice(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fatura fotoğrafı yükle ve OCR işlemi yap"""
    try:
        # File validation
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        # Read file
        contents = await file.read()
        
        # OCR processing
        ocr_result = ocr_service.process_invoice(contents)
        
        # Save to database
        invoice_data = InvoiceCreate(
            filename=file.filename,
            ocr_data=ocr_result,
            user_id=current_user.id
        )
        
        invoice = invoice_service.create_invoice(invoice_data, db)
        
        return InvoiceResponse.model_validate(invoice)
    
    except Exception as e:
        print(f"Invoice processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing invoice: {str(e)}")

@app.get("/invoices", response_model=List[InvoiceResponse])
async def get_user_invoices(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının işlem görmüş faturalarını getir"""
    try:
        print(f"🔍 Kullanıcı {current_user.id} için faturalar getiriliyor...")
        invoices = invoice_service.get_user_invoices(current_user.id, db)
        print(f"✅ {len(invoices)} fatura bulundu")
        
        # Her faturayı validate et
        validated_invoices = []
        for i, invoice in enumerate(invoices):
            try:
                validated_invoice = InvoiceResponse.model_validate(invoice)
                validated_invoices.append(validated_invoice)
            except Exception as e:
                print(f"❌ Fatura {i} validate edilemedi: {e}")
                print(f"Fatura verisi: {invoice}")
                # Hatalı faturayı atla ama devam et
                continue
        
        print(f"✅ {len(validated_invoices)} fatura başarıyla validate edildi")
        return validated_invoices
        
    except Exception as e:
        print(f"❌ Faturalar getirilirken hata: {e}")
        raise HTTPException(status_code=500, detail=f"Faturalar getirilirken hata oluştu: {str(e)}")

@app.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Belirli bir faturanın detaylarını getir"""
    invoice = invoice_service.get_invoice(invoice_id, current_user.id, db)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceResponse.model_validate(invoice)

@app.post("/debug/ocr")
async def debug_ocr(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """OCR debug endpoint - ham OCR sonucunu döndürür"""
    try:
        contents = await file.read()
        ocr_result = ocr_service.process_invoice(contents)
        return {
            "raw_text": ocr_result.get("raw_text", ""),
            "extracted_data": ocr_result.get("extracted_data", {}),
            "error": ocr_result.get("error", None)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/invoices/export/excel")
async def export_invoices_excel(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fatura verilerini Excel formatında export et"""
    try:
        # Tarih filtresi uygula
        invoices = invoice_service.get_user_invoices_with_date_filter(
            current_user.id, 
            start_date, 
            end_date, 
            db
        )
        excel_data = excel_service.create_excel_export(invoices)
        
        from fastapi.responses import StreamingResponse
        
        # Dosya adını tarih filtresine göre ayarla
        filename = "invoices"
        if start_date and end_date:
            filename = f"invoices_{start_date}_to_{end_date}"
        elif start_date:
            filename = f"invoices_from_{start_date}"
        elif end_date:
            filename = f"invoices_until_{end_date}"
        else:
            filename = f"invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting Excel: {str(e)}")

# User profile endpoints
@app.get("/user/profile", response_model=UserResponse)
async def get_profile(current_user = Depends(get_current_user)):
    """Kullanıcı profil bilgilerini getir"""
    return UserResponse.model_validate(current_user)

@app.put("/user/profile", response_model=UserResponse)
async def update_profile(
    profile_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcı profil bilgilerini güncelle"""
    try:
        updated_user = auth_service.update_user_profile(current_user.id, profile_data, db)
        return UserResponse.model_validate(updated_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
