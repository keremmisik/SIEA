import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

// Set base URL for mobile access on same network
const getBaseURL = () => {
  // If we're on localhost, use localhost
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // If we're on a mobile device or different IP, use the current hostname
  const currentHost = window.location.hostname;
  return `http://${currentHost}:8000`;
};

const baseURL = getBaseURL();
axios.defaults.baseURL = baseURL;
console.log('Axios base URL set to:', baseURL);
console.log('Current hostname:', window.location.hostname);

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
          console.log('Checking auth with token:', token.substring(0, 20) + '...');
          const response = await axios.get('/user/profile');
          setUser(response.data);
          console.log('Auth check successful:', response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          console.error('Error response:', error.response);
          logout();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (email, password) => {
    try {
      console.log('Login attempt:', { email, password: '***' });
      const response = await axios.post('/auth/login', {
        email,
        password
      });

      const { access_token } = response.data;
      console.log('Login successful, token received');
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Get user profile
      const profileResponse = await axios.get('/user/profile');
      setUser(profileResponse.data);
      console.log('User profile loaded:', profileResponse.data);
      
      toast.success('Başarıyla giriş yapıldı!');
      return true;
    } catch (error) {
      console.error('Login error:', error);
      console.error('Error response:', error.response);
      const message = error.response?.data?.detail || error.message || 'Giriş yapılırken hata oluştu';
      toast.error(message);
      return false;
    }
  };

  const register = async (fullName, email, password) => {
    try {
      console.log('Register attempt:', { fullName, email, password: '***' });
      await axios.post('/auth/register', {
        full_name: fullName,
        email,
        password
      });
      
      console.log('Registration successful');
      toast.success('Hesap başarıyla oluşturuldu! Giriş yapabilirsiniz.');
      return true;
    } catch (error) {
      console.error('Register error:', error);
      console.error('Error response:', error.response);
      const message = error.response?.data?.detail || error.message || 'Kayıt olurken hata oluştu';
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
