import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { User, Mail, Calendar, Edit2, Save, X } from 'lucide-react';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || ''
  });
  const [loading, setLoading] = useState(false);

  const handleEdit = () => {
    setIsEditing(true);
    setFormData({
      full_name: user?.full_name || ''
    });
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      full_name: user?.full_name || ''
    });
  };

  const handleSave = async () => {
    setLoading(true);
    const success = await updateProfile(formData);
    
    if (success) {
      setIsEditing(false);
    }
    
    setLoading(false);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="h-12 w-12 rounded-full bg-primary-100 flex items-center justify-center">
                <User className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-900">Profil Bilgileri</h1>
                <p className="text-sm text-gray-600">Hesap bilgilerinizi görüntüleyin ve düzenleyin</p>
              </div>
            </div>
            
            {!isEditing ? (
              <button
                onClick={handleEdit}
                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <Edit2 className="w-4 h-4 mr-2" />
                Düzenle
              </button>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={handleCancel}
                  disabled={loading}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
                >
                  <X className="w-4 h-4 mr-2" />
                  İptal
                </button>
                <button
                  onClick={handleSave}
                  disabled={loading}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  ) : (
                    <Save className="w-4 h-4 mr-2" />
                  )}
                  Kaydet
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Profile Content */}
        <div className="px-6 py-6">
          <div className="space-y-6">
            {/* Personal Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Kişisel Bilgiler</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Full Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ad Soyad
                  </label>
                  {isEditing ? (
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <User className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        value={formData.full_name}
                        onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                        placeholder="Ad Soyadınız"
                      />
                    </div>
                  ) : (
                    <div className="flex items-center p-3 bg-gray-50 rounded-md">
                      <User className="h-5 w-5 text-gray-400 mr-3" />
                      <span className="text-sm text-gray-900">{user?.full_name}</span>
                    </div>
                  )}
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    E-posta Adresi
                  </label>
                  <div className="flex items-center p-3 bg-gray-50 rounded-md">
                    <Mail className="h-5 w-5 text-gray-400 mr-3" />
                    <span className="text-sm text-gray-900">{user?.email}</span>
                    <span className="ml-2 px-2 py-1 text-xs bg-gray-200 text-gray-600 rounded-full">
                      Değiştirilemez
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Account Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Hesap Bilgileri</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Account Status */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hesap Durumu
                  </label>
                  <div className="flex items-center p-3 bg-gray-50 rounded-md">
                    <div className={`h-3 w-3 rounded-full mr-3 ${user?.is_active ? 'bg-green-400' : 'bg-red-400'}`}></div>
                    <span className="text-sm text-gray-900">
                      {user?.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                  </div>
                </div>

                {/* Member Since */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Üyelik Tarihi
                  </label>
                  <div className="flex items-center p-3 bg-gray-50 rounded-md">
                    <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                    <span className="text-sm text-gray-900">
                      {user?.created_at ? formatDate(user.created_at) : '-'}
                    </span>
                  </div>
                </div>

                {/* Last Updated */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Son Güncelleme
                  </label>
                  <div className="flex items-center p-3 bg-gray-50 rounded-md">
                    <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                    <span className="text-sm text-gray-900">
                      {user?.updated_at ? formatDate(user.updated_at) : '-'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Security Notice */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">
                    Güvenlik Bildirimi
                  </h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <p>
                      Tüm fatura verileriniz şifreli olarak saklanmakta ve maksimum 5 yıl süreyle tutulmaktadır. 
                      Bu süre sonunda verileriniz otomatik olarak sistemden silinecektir.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
