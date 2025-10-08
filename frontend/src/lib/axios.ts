import axios from 'axios';

// Configure axios defaults for API communication
const setupAxios = () => {
  // Set base URL for API requests
  axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  
  // Set default headers
  axios.defaults.headers.common['Content-Type'] = 'application/json';
  
  // Add request interceptor for debugging
  axios.interceptors.request.use(
    (config) => {
      console.log('🌐 API Request:', config.method?.toUpperCase(), config.url);
      return config;
    },
    (error) => {
      console.error('❌ API Request Error:', error);
      return Promise.reject(error);
    }
  );

  // Add response interceptor for debugging
  axios.interceptors.response.use(
    (response) => {
      console.log('✅ API Response:', response.status, response.config.url);
      return response;
    },
    (error) => {
      console.error('❌ API Response Error:', {
        status: error.response?.status,
        url: error.config?.url,
        message: error.message,
        data: error.response?.data,
      });
      return Promise.reject(error);
    }
  );
};

export { setupAxios };