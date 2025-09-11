import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import { useDropzone } from 'react-dropzone';
import { Camera, Upload, RotateCcw, Check, X, Image as ImageIcon, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { toast } from 'react-toastify';

const Scanner = () => {
  const [mode, setMode] = useState('camera'); // 'camera' or 'upload'
  const [capturedImage, setCapturedImage] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [cameraError, setCameraError] = useState(null);
  const [isHttps, setIsHttps] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);

  // HTTPS kontrolü ve mobil tespiti
  useEffect(() => {
    setIsHttps(window.location.protocol === 'https:');
    setIsMobile(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent));
  }, []);

  // Dinamik kamera ayarları - hem web hem mobil için
  const getVideoConstraints = () => {
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isMobile) {
      // Mobil için esnek ayarlar
      return {
        width: { ideal: 1920, max: 1920, min: 320 },
        height: { ideal: 1080, max: 1080, min: 240 },
        facingMode: "environment" // Arka kamera tercih et ama zorunlu değil
      };
    } else {
      // Desktop için ayarlar
      return {
        width: { ideal: 1280, max: 1920, min: 640 },
        height: { ideal: 720, max: 1080, min: 480 },
        facingMode: "user" // Ön kamera (webcam)
      };
    }
  };

  const [videoConstraints, setVideoConstraints] = useState(getVideoConstraints());

  // Kamera ile fotoğraf çek
  const capture = useCallback(() => {
    // Mobil cihazda ve HTTP'de telefon kamerasını aç
    if (isMobile && !isHttps) {
      fileInputRef.current.click();
      return;
    }
    
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
  }, [webcamRef, isMobile, isHttps]);

  // Fotoğrafı tekrar çek
  const retake = () => {
    setCapturedImage(null);
    setResult(null);
  };

  // Kamera hatası yakalama
  const handleCameraError = (error) => {
    console.error('Kamera hatası:', error);
    setCameraError(error.message || 'Kameraya erişim sağlanamadı');
    
    // Eğer environment kamera bulunamazsa user kamerayı dene
    if (error.name === 'OverconstrainedError' || error.message.includes('environment')) {
      console.log('Arka kamera bulunamadı, ön kameraya geçiliyor...');
      setVideoConstraints({
        width: { ideal: 1280, max: 1920, min: 640 },
        height: { ideal: 720, max: 1080, min: 480 },
        facingMode: "user"
      });
      setCameraError(null);
    } else {
      toast.error('Kamera erişimi engellenmiş. Lütfen tarayıcı ayarlarınızı kontrol edin.');
    }
  };

  // Kamera değiştirme fonksiyonu
  const switchCamera = () => {
    const currentFacing = videoConstraints.facingMode;
    const newConstraints = {
      ...videoConstraints,
      facingMode: currentFacing === "environment" ? "user" : "environment"
    };
    setVideoConstraints(newConstraints);
    setCameraError(null);
  };

  // Dosya yükleme için dropzone
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCapturedImage(e.target.result);
        setMode('upload');
      };
      reader.readAsDataURL(file);
    }
  }, []);

  // Telefon kamerasından gelen dosyayı işle
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCapturedImage(e.target.result);
        setMode('camera');
      };
      reader.readAsDataURL(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.gif']
    },
    multiple: false
  });

  // Faturayı işle
  const processInvoice = async () => {
    if (!capturedImage) return;

    setProcessing(true);
    setResult(null);

    try {
      // Base64 string'i blob'a çevir
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      
      // FormData oluştur
      const formData = new FormData();
      formData.append('file', blob, 'invoice.jpg');

      // API'ye gönder
      const apiResponse = await axios.post('/invoices/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(apiResponse.data);
      toast.success('Fatura başarıyla işlendi!');
      
    } catch (error) {
      console.error('Processing error:', error);
      const message = error.response?.data?.detail || 'Fatura işlenirken hata oluştu';
      toast.error(message);
    } finally {
      setProcessing(false);
    }
  };

  // Yeni tarama başlat
  const startNewScan = () => {
    setCapturedImage(null);
    setResult(null);
    setMode('camera');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">Fatura Tarama</h1>
          <p className="text-sm text-gray-600 mt-1">
            Faturanızı kamera ile tarayın veya fotoğraf yükleyin
          </p>
        </div>

        {/* Mode Selection */}
        {!capturedImage && (
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex space-x-4">
              <button
                onClick={() => setMode('camera')}
                className={`flex items-center px-4 py-2 rounded-md text-sm font-medium ${
                  mode === 'camera'
                    ? 'bg-primary-100 text-primary-700 border-primary-300'
                    : 'bg-gray-100 text-gray-700 border-gray-300'
                } border`}
              >
                <Camera className="w-4 h-4 mr-2" />
                Kamera
              </button>
              <button
                onClick={() => setMode('upload')}
                className={`flex items-center px-4 py-2 rounded-md text-sm font-medium ${
                  mode === 'upload'
                    ? 'bg-primary-100 text-primary-700 border-primary-300'
                    : 'bg-gray-100 text-gray-700 border-gray-300'
                } border`}
              >
                <Upload className="w-4 h-4 mr-2" />
                Dosya Yükle
              </button>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="p-6">
          {!capturedImage ? (
            <div className="space-y-6">
              {/* HTTP/HTTPS Bilgi - Sadece kamera modunda göster */}
              {!isHttps && mode === 'camera' && (
                <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
                  <div className="flex">
                    <AlertCircle className="h-5 w-5 text-blue-400" />
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-blue-800">
                        HTTP Modu - Kamera Sınırlı
                      </h3>
                      <div className="mt-2 text-sm text-blue-700">
                        <p>HTTP'de kamera erişimi sınırlıdır. HTTPS için <code>npm run start:https</code> kullanın veya dosya yükleme moduna geçin.</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Camera Mode */}
              {mode === 'camera' && (
                <div className="text-center">
                  {/* Gizli dosya input - mobil kamera için */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    capture="environment"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                  />
                  
                  {/* Webcam - sadece HTTPS'de veya desktop'ta göster */}
                  {(!isMobile || isHttps) && (
                    <div className="relative inline-block rounded-lg overflow-hidden shadow-lg">
                      <Webcam
                        audio={false}
                        ref={webcamRef}
                        screenshotFormat="image/jpeg"
                        videoConstraints={videoConstraints}
                        onUserMediaError={handleCameraError}
                        className="w-full max-w-2xl"
                      />
                    </div>
                  )}
                  
                  {/* Mobil HTTP modunda kamera bilgisi */}
                  {isMobile && !isHttps && (
                    <div className="py-12">
                      <Camera className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Telefon Kamerası
                      </h3>
                      <p className="text-gray-600 mb-6">
                        HTTP modunda telefon kamerasını kullanarak fotoğraf çekin
                      </p>
                    </div>
                  )}
                  
                  <div className="mt-4 space-x-4">
                    <button
                      onClick={capture}
                      className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      <Camera className="w-5 h-5 mr-2" />
                      {isMobile && !isHttps ? 'Telefon Kamerasını Aç' : 'Fotoğraf Çek'}
                    </button>
                    {(!isMobile || isHttps) && (
                      <button
                        onClick={switchCamera}
                        className="inline-flex items-center px-4 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                      >
                        <RotateCcw className="w-5 h-5 mr-2" />
                        Kamera Değiştir
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Upload Mode */}
              {mode === 'upload' && (
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                    isDragActive
                      ? 'border-primary-400 bg-primary-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <input {...getInputProps()} />
                  <ImageIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-2 text-lg font-medium text-gray-900">
                    {isDragActive
                      ? 'Dosyayı buraya bırakın'
                      : 'Fatura fotoğrafı yükleyin'}
                  </p>
                  <p className="mt-1 text-sm text-gray-600">
                    Dosyayı sürükleyip bırakın veya seçmek için tıklayın
                  </p>
                  <p className="mt-1 text-xs text-gray-500">
                    JPG, JPEG, PNG, BMP, GIF (Max 10MB)
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Captured Image */}
              <div className="text-center">
                <div className="relative inline-block rounded-lg overflow-hidden shadow-lg">
                  <img
                    src={capturedImage}
                    alt="Captured invoice"
                    className="max-w-full max-h-96 object-contain"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-center space-x-4">
                <button
                  onClick={retake}
                  disabled={processing}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Tekrar Çek
                </button>
                <button
                  onClick={processInvoice}
                  disabled={processing}
                  className="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {processing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      İşleniyor...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4 mr-2" />
                      Faturayı İşle
                    </>
                  )}
                </button>
              </div>

              {/* Processing Result */}
              {result && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <div className="flex items-center mb-4">
                    <Check className="w-5 h-5 text-green-600 mr-2" />
                    <h3 className="text-lg font-medium text-green-800">
                      Fatura Başarıyla İşlendi
                    </h3>
                  </div>
                  
                  {/* Basic Invoice Info */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mb-6">
                    {result.invoice_number && (
                      <div>
                        <span className="font-medium text-gray-700">Fatura No:</span>
                        <span className="ml-2 text-gray-900">{result.invoice_number}</span>
                      </div>
                    )}
                    {result.company_name && (
                      <div>
                        <span className="font-medium text-gray-700">Şirket:</span>
                        <span className="ml-2 text-gray-900">{result.company_name}</span>
                      </div>
                    )}
                    {result.total_amount && (
                      <div>
                        <span className="font-medium text-gray-700">Toplam:</span>
                        <span className="ml-2 text-gray-900">{result.total_amount}</span>
                      </div>
                    )}
                    {result.invoice_date && (
                      <div>
                        <span className="font-medium text-gray-700">Tarih:</span>
                        <span className="ml-2 text-gray-900">
                          {new Date(result.invoice_date).toLocaleDateString('tr-TR')}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Multiple Products Display */}
                  {result.has_multiple_products && result.products_data && result.products_data.length > 0 ? (
                    <div className="mb-6">
                      <h4 className="text-md font-semibold text-gray-800 mb-3">Ürün Detayları</h4>
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
                            {result.products_data.map((product, index) => (
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
                  ) : (
                    /* Single Product or Traditional Display */
                    <div className="mb-6">
                      <h4 className="text-md font-semibold text-gray-800 mb-3">Fatura Özeti</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        {result.tax_rate && (
                          <div>
                            <span className="font-medium text-gray-700">KDV Oranı:</span>
                            <span className="ml-2 text-gray-900">%{result.tax_rate}</span>
                          </div>
                        )}
                        {result.tax_amount && (
                          <div>
                            <span className="font-medium text-gray-700">KDV Tutarı:</span>
                            <span className="ml-2 text-gray-900">{result.tax_amount} TL</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="mt-4">
                    <button
                      onClick={startNewScan}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      Yeni Fatura Tara
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Scanner;
