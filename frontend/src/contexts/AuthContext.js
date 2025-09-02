import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

// Set base URL for mobile access
axios.defaults.baseURL = process.env.NODE_ENV === 'production' 
  ? 'http://10.203.71.91:8000'
  : 'http://10.203.71.91:8000';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Axios interceptor for adding token to requests
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await axios.get('/user/profile');
          setUser(response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          logout();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await axios.post('/auth/login', {
        email,
        password
      });

      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Get user profile
      const profileResponse = await axios.get('/user/profile');
      setUser(profileResponse.data);
      
      toast.success('Başarıyla giriş yapıldı!');
      return true;
    } catch (error) {
      const message = error.response?.data?.detail || 'Giriş yapılırken hata oluştu';
      toast.error(message);
      return false;
    }
  };

  const register = async (fullName, email, password) => {
    try {
      await axios.post('/auth/register', {
        full_name: fullName,
        email,
        password
      });
      
      toast.success('Hesap başarıyla oluşturuldu! Giriş yapabilirsiniz.');
      return true;
    } catch (error) {
      const message = error.response?.data?.detail || 'Kayıt olurken hata oluştu';
      toast.error(message);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
    toast.info('Çıkış yapıldı');
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put('/user/profile', profileData);
      setUser(response.data);
      toast.success('Profil başarıyla güncellendi!');
      return true;
    } catch (error) {
      const message = error.response?.data?.detail || 'Profil güncellenirken hata oluştu';
      toast.error(message);
      return false;
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    updateProfile,
    loading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
