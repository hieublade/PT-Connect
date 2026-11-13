import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ptconnect_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => {
    // If response is envelope: { status, message, data }
    if (response.data && 'data' in response.data) {
      return response.data.data;
    }
    return response.data;
  },
  (error) => {
    const requestUrl = error.config?.url || '';
    const isAuthEndpoint = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register');

    if (error.response?.status === 401 && !isAuthEndpoint) {
      const hadToken = !!localStorage.getItem('ptconnect_token');
      localStorage.removeItem('ptconnect_token');
      localStorage.removeItem('ptconnect_user');
      if (hadToken) {
        window.location.reload();
      }
    }
    const message = error.response?.data?.message || error.message || 'Lỗi kết nối';
    return Promise.reject(new Error(message));
  }
);

export default api;
