import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { 
  Download, 
  FileText, 
  Calendar, 
  Building, 
  DollarSign, 
  Search,
  Filter,
  Eye,
  Trash2
} from 'lucide-react';

const ProcessedInvoices = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [dateFilter, setDateFilter] = useState({
    startDate: '',
    endDate: '',
    enabled: false
  });

  // Faturaları yükle
  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/invoices');
      setInvoices(response.data);
      console.log('✅ Faturalar başarıyla yüklendi:', response.data.length);
    } catch (error) {
      console.error('❌ Faturalar yüklenirken hata:', error);
      console.error('Hata detayları:', error.response?.data);
      toast.error(`Faturalar yüklenirken hata oluştu: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Excel export
  const exportToExcel = async () => {
    try {
      // Tarih filtresi parametrelerini hazırla
      const params = new URLSearchParams();
      if (dateFilter.enabled && dateFilter.startDate) {
        params.append('start_date', dateFilter.startDate);
      }
      if (dateFilter.enabled && dateFilter.endDate) {
        params.append('end_date', dateFilter.endDate);
      }
      
      const url = `/invoices/export/excel${params.toString() ? '?' + params.toString() : ''}`;
      const response = await axios.get(url, {
        responseType: 'blob',
      });
      
      // Blob'u indirilebilir link'e çevir
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      
      // Dosya adını tarih filtresine göre ayarla
      let filename = 'faturalar';
      if (dateFilter.enabled && dateFilter.startDate && dateFilter.endDate) {
        filename = `faturalar_${dateFilter.startDate}_${dateFilter.endDate}`;
      } else if (dateFilter.enabled && dateFilter.startDate) {
        filename = `faturalar_${dateFilter.startDate}_sonrası`;
      } else if (dateFilter.enabled && dateFilter.endDate) {
        filename = `faturalar_${dateFilter.endDate}_öncesi`;
      } else {
        filename = `faturalar_${new Date().toISOString().split('T')[0]}`;
      }
      
      link.download = `${filename}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      
      toast.success('Excel dosyası başarıyla indirildi!');
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Excel export edilirken hata oluştu');
    }
  };

  // Fatura detaylarını göster
  const showInvoiceDetails = (invoice) => {
    setSelectedInvoice(invoice);
    setShowModal(true);
  };

  // Filtreleme ve sıralama
  const filteredAndSortedInvoices = invoices
    .filter(invoice => {
      // Metin arama filtresi
      const matchesSearch = invoice.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        invoice.invoice_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        invoice.filename?.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Tarih filtresi
      let matchesDate = true;
      if (dateFilter.enabled) {
        const invoiceDate = new Date(invoice.created_at);
        
        if (dateFilter.startDate) {
          const startDate = new Date(dateFilter.startDate);
          matchesDate = matchesDate && invoiceDate >= startDate;
        }
        
        if (dateFilter.endDate) {
          const endDate = new Date(dateFilter.endDate);
          endDate.setHours(23, 59, 59, 999); // Gün sonuna kadar dahil et
          matchesDate = matchesDate && invoiceDate <= endDate;
        }
      }
      
      return matchesSearch && matchesDate;
    })
    .sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (sortBy === 'created_at' || sortBy === 'invoice_date') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount) => {
    if (!amount) return '-';
    return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".") + ' ₺';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">İşlem Görmüş Faturalar</h1>
              <p className="text-sm text-gray-600 mt-1">
                {dateFilter.enabled ? (
                  <>
                    {filteredAndSortedInvoices.length} fatura gösteriliyor 
                    (Toplam {invoices.length} faturadan)
                    {dateFilter.startDate && dateFilter.endDate && (
                      <span className="ml-1 text-blue-600">
                        ({dateFilter.startDate} - {dateFilter.endDate})
                      </span>
                    )}
                  </>
                ) : (
                  `Toplam ${invoices.length} fatura işlendi`
                )}
              </p>
            </div>
            <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row gap-3">
              {/* Tarih Filtresi */}
              <div className="flex items-center space-x-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={dateFilter.enabled}
                    onChange={(e) => setDateFilter(prev => ({ ...prev, enabled: e.target.checked }))}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Tarih Filtresi</span>
                </label>
              </div>
              
              {dateFilter.enabled && (
                <div className="flex items-center space-x-2">
                  <input
                    type="date"
                    value={dateFilter.startDate}
                    onChange={(e) => setDateFilter(prev => ({ ...prev, startDate: e.target.value }))}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Başlangıç tarihi"
                  />
                  <span className="text-gray-500">-</span>
                  <input
                    type="date"
                    value={dateFilter.endDate}
                    onChange={(e) => setDateFilter(prev => ({ ...prev, endDate: e.target.value }))}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Bitiş tarihi"
                  />
                </div>
              )}
              
              <button
                onClick={exportToExcel}
                disabled={invoices.length === 0}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-4 h-4 mr-2" />
                Excel İndir
              </button>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0 sm:space-x-4">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Şirket adı, fatura no veya dosya adı ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>

            {/* Sort */}
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={`${sortBy}-${sortOrder}`}
                onChange={(e) => {
                  const [field, order] = e.target.value.split('-');
                  setSortBy(field);
                  setSortOrder(order);
                }}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
              >
                <option value="created_at-desc">Yeni → Eski</option>
                <option value="created_at-asc">Eski → Yeni</option>
                <option value="company_name-asc">Şirket A → Z</option>
                <option value="company_name-desc">Şirket Z → A</option>
                <option value="total_amount-desc">Tutar Büyük → Küçük</option>
                <option value="total_amount-asc">Tutar Küçük → Büyük</option>
              </select>
            </div>
          </div>
        </div>

        {/* Invoice List */}
        {filteredAndSortedInvoices.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              {searchTerm ? 'Arama kriterinize uygun fatura bulunamadı' : 'Henüz fatura yok'}
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm ? 'Farklı terimlerle arama yapın' : 'İlk faturanızı taramak için scanner sayfasına gidin'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-blue-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-blue-700 uppercase tracking-wider">
                    🏢 Şirket Adı
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-blue-700 uppercase tracking-wider">
                    🎯 Fatura No
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-blue-700 uppercase tracking-wider">
                    💰 Toplam Tutar
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-blue-700 uppercase tracking-wider">
                    📊 KDV Tutarı
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-blue-700 uppercase tracking-wider">
                    📈 KDV Oranı
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    📅 Tarih
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    İşlem
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAndSortedInvoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    {/* Şirket Adı - 1. Sütun */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      {invoice.company_name ? (
                        <div className="flex items-center">
                          <Building className="h-4 w-4 text-green-500 mr-2" />
                          <span className="text-sm font-medium text-gray-900">
                            {invoice.company_name}
                          </span>
                        </div>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          ❌ Tespit edilemedi
                        </span>
                      )}
                    </td>
                    
                    {/* Fatura No - 2. Sütun */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      {invoice.invoice_number ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                          ✅ {invoice.invoice_number}
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          ❌ Tespit edilemedi
                        </span>
                      )}
                    </td>
                    
                    {/* Toplam Tutar - 3. Sütun */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      {invoice.total_amount ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                          ✅ {invoice.total_amount} TL
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          ❌ Tespit edilemedi
                        </span>
                      )}
                    </td>
                    
                    {/* KDV Tutarı - 4. Sütun */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      {invoice.tax_amount ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                          ✅ {invoice.tax_amount} TL
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          ❌ Tespit edilemedi
                        </span>
                      )}
                    </td>
                    
                    {/* KDV Oranı - 5. Sütun */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      {invoice.has_multiple_products && invoice.products_data && invoice.products_data.length > 0 ? (
                        <div className="space-y-1">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            📦 Çoklu Ürün
                          </span>
                          <div className="text-xs text-gray-600">
                            {invoice.products_data.length} ürün
                          </div>
                        </div>
                      ) : invoice.tax_rate ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                          ✅ %{invoice.tax_rate}
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          ❌ Tespit edilemedi
                        </span>
                      )}
                    </td>
                    
                    {/* Tarih - 6. Sütun */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                        <div>
                          <div className="text-sm text-gray-900">
                            {invoice.invoice_date 
                              ? new Date(invoice.invoice_date).toLocaleDateString('tr-TR')
                              : '-'
                            }
                          </div>
                          <div className="text-xs text-gray-500">
                            İşlendi: {formatDate(invoice.created_at)}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => showInvoiceDetails(invoice)}
                        className="text-primary-600 hover:text-primary-900 mr-3"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal for invoice details */}
      {showModal && selectedInvoice && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-2xl shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Fatura Detayları</h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <span className="sr-only">Kapat</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Fatura No</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedInvoice.invoice_number || '-'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Şirket Adı</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedInvoice.company_name || '-'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Toplam Tutar</label>
                  <p className="mt-1 text-sm text-gray-900">{formatCurrency(selectedInvoice.total_amount)}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">KDV Tutarı</label>
                  <p className="mt-1 text-sm text-gray-900">{formatCurrency(selectedInvoice.tax_amount)}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">KDV Oranı</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedInvoice.tax_rate ? `%${selectedInvoice.tax_rate}` : '-'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Fatura Tarihi</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {selectedInvoice.invoice_date 
                      ? new Date(selectedInvoice.invoice_date).toLocaleDateString('tr-TR')
                      : '-'
                    }
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">İşlem Tarihi</label>
                  <p className="mt-1 text-sm text-gray-900">{formatDate(selectedInvoice.created_at)}</p>
                </div>
              </div>

              {/* Multiple Products Display in Modal */}
              {selectedInvoice.has_multiple_products && selectedInvoice.products_data && selectedInvoice.products_data.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">Ürün Detayları</label>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Ürün Adı
                          </th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Miktar
                          </th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Birim Fiyat
                          </th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Toplam Fiyat
                          </th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            KDV Oranı
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {selectedInvoice.products_data.map((product, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                              {product.product_name || '-'}
                            </td>
                            <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                              {product.quantity || '1'}
                            </td>
                            <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                              {product.unit_price ? `${product.unit_price} TL` : '-'}
                            </td>
                            <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                              {product.total_price ? `${product.total_price} TL` : '-'}
                            </td>
                            <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                              {product.tax_rate ? `%${product.tax_rate}` : '-'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Dosya Adı</label>
                <p className="mt-1 text-sm text-gray-900">{selectedInvoice.filename}</p>
              </div>

              {/* OCR Raw Text */}
              {selectedInvoice.ocr_data?.raw_text && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Ham OCR Metni</label>
                  <div className="mt-1 p-3 bg-gray-50 rounded-md max-h-32 overflow-y-auto">
                    <p className="text-xs text-gray-700 whitespace-pre-wrap">
                      {selectedInvoice.ocr_data.raw_text}
                    </p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex justify-end mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Kapat
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProcessedInvoices;
