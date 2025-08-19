import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { showMessage } from '$lib/utils/utils';

// Create axios instance
const request: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 60000,
  withCredentials: true,
});

// Request interceptor
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data } = response;
    
    // Handle different response codes
    if (data.code && data.code !== 200) {
      const message = showMessage();
      if (message) {
        message.error(data.message || 'Request failed');
      }
      return Promise.reject(new Error(data.message || 'Request failed'));
    }
    
    return data;
  },
  (error) => {
    const message = showMessage();
    if (message) {
      if (error.response?.status === 401) {
        message.error('Authentication failed, please login again');
        // Redirect to login if needed
      } else if (error.response?.status === 403) {
        message.error('Permission denied');
      } else if (error.response?.status === 404) {
        message.error('Resource not found');
      } else if (error.response?.status >= 500) {
        message.error('Server error, please try again later');
      } else {
        message.error(error.message || 'Network error');
      }
    }
    
    return Promise.reject(error);
  }
);

export default request;