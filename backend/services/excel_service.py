import pandas as pd
import io
from datetime import datetime
from typing import List
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

from database.models import Invoice

class ExcelService:
    def __init__(self):
        pass
    
    def create_excel_export(self, invoices: List[Invoice]) -> bytes:
        """Fatura listesinden Excel dosyası oluştur"""
        try:
            # Fatura verilerini DataFrame'e çevir
            data = []
            for invoice in invoices:
                ocr_data = invoice.ocr_data or {}
                extracted_data = ocr_data.get('extracted_data', {})
                
                row = {
                    'Fatura No': invoice.invoice_number or extracted_data.get('invoice_number', ''),
                    'Şirket Adı': invoice.company_name or extracted_data.get('company_name', ''),
                    'Fatura Tarihi': invoice.invoice_date.strftime('%d.%m.%Y') if invoice.invoice_date else extracted_data.get('invoice_date', ''),
                    'Toplam Tutar': invoice.total_amount or extracted_data.get('total_amount', ''),
                    'KDV Tutarı': invoice.tax_amount or extracted_data.get('tax_amount', ''),
                    'Dosya Adı': invoice.filename,
                    'İşlem Tarihi': invoice.processed_at.strftime('%d.%m.%Y %H:%M') if invoice.processed_at else '',
                    'Oluşturma Tarihi': invoice.created_at.strftime('%d.%m.%Y %H:%M') if invoice.created_at else ''
                }
                data.append(row)
            
            # DataFrame oluştur
            df = pd.DataFrame(data)
            
            # Excel dosyası oluştur
            return self._create_styled_excel(df, invoices)
            
        except Exception as e:
            raise Exception(f"Excel export failed: {str(e)}")
    
    def _create_styled_excel(self, df: pd.DataFrame, invoices: List[Invoice]) -> bytes:
        """Stillendirilmiş Excel dosyası oluştur"""
        # Workbook oluştur
        wb = Workbook()
        ws = wb.active
        ws.title = "Faturalar"
        
        # Başlık ekle
        title = f"FATURA LİSTESİ - {datetime.now().strftime('%d.%m.%Y')}"
        ws['A1'] = title
        ws['A1'].font = Font(size=16, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center')
        ws.merge_cells('A1:H1')
        
        # İstatistikler ekle
        ws['A3'] = f"Toplam Fatura Sayısı: {len(invoices)}"
        ws['A3'].font = Font(bold=True)
        
        # DataFrame'i Excel'e aktar (5. satırdan başla)
        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)
        
        # Başlık satırını stillendir
        header_row = 5
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        
        for col in range(1, len(df.columns) + 1):
            cell = ws.cell(row=header_row, column=col)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Sütun genişliklerini ayarla
        column_widths = {
            'A': 15,  # Fatura No
            'B': 30,  # Şirket Adı
            'C': 12,  # Fatura Tarihi
            'D': 15,  # Toplam Tutar
            'E': 12,  # KDV Tutarı
            'F': 25,  # Dosya Adı
            'G': 18,  # İşlem Tarihi
            'H': 18   # Oluşturma Tarihi
        }
        
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width
        
        # Veri satırlarını stillendir
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Tüm veri hücrelerine border ekle
        for row in range(header_row, header_row + len(df) + 1):
            for col in range(1, len(df.columns) + 1):
                cell = ws.cell(row=row, column=col)
                cell.border = thin_border
                cell.alignment = Alignment(vertical='center')
        
        # Alternatif satır renkleri
        light_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        for row in range(header_row + 2, header_row + len(df) + 1, 2):
            for col in range(1, len(df.columns) + 1):
                ws.cell(row=row, column=col).fill = light_fill
        
        # Özet sayfa ekle
        summary_ws = wb.create_sheet(title="Özet")
        self._create_summary_sheet(summary_ws, invoices)
        
        # Excel dosyasını bytes olarak döndür
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        return excel_buffer.getvalue()
    
    def _create_summary_sheet(self, ws, invoices: List[Invoice]):
        """Özet sayfası oluştur"""
        # Başlık
        ws['A1'] = "FATURA ÖZETİ"
        ws['A1'].font = Font(size=16, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center')
        ws.merge_cells('A1:D1')
        
        # İstatistikler
        stats = [
            ["Toplam Fatura Sayısı", len(invoices)],
            ["Bu Ay İşlenen", len([inv for inv in invoices if inv.created_at.month == datetime.now().month])],
            ["En Eski Fatura", min(invoices, key=lambda x: x.created_at).created_at.strftime('%d.%m.%Y') if invoices else ""],
            ["En Yeni Fatura", max(invoices, key=lambda x: x.created_at).created_at.strftime('%d.%m.%Y') if invoices else ""]
        ]
        
        for i, (label, value) in enumerate(stats, start=3):
            ws[f'A{i}'] = label
            ws[f'B{i}'] = value
            ws[f'A{i}'].font = Font(bold=True)
        
        # Şirket bazında özet
        ws['A8'] = "ŞİRKET BAZINDA ÖZET"
        ws['A8'].font = Font(size=14, bold=True)
        
        # Şirketleri grupla
        companies = {}
        for invoice in invoices:
            company = invoice.company_name or "Bilinmeyen Şirket"
            companies[company] = companies.get(company, 0) + 1
        
        ws['A10'] = "Şirket Adı"
        ws['B10'] = "Fatura Sayısı"
        ws['A10'].font = Font(bold=True)
        ws['B10'].font = Font(bold=True)
        
        for i, (company, count) in enumerate(sorted(companies.items()), start=11):
            ws[f'A{i}'] = company
            ws[f'B{i}'] = count
        
        # Sütun genişliklerini ayarla
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 15
