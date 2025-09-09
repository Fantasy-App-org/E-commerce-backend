import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API Services
export const apiService = {
  // Product APIs
  getProducts: (params = {}) => api.get('/products/', { params }),
  getProduct: (slug) => api.get(`/products/${slug}/`),
  getCategories: () => api.get('/categories/'),
  
  // Cart APIs
  getCart: () => api.get('/cart/'),
  addToCart: (data) => api.post('/cart/add/', data),
  updateCartItem: (data) => api.patch('/cart/update_item/', data),
  clearCart: () => api.delete('/cart/clear/'),
  
  // Order APIs
  getOrders: () => api.get('/orders/'),
  createOrder: () => api.post('/orders/create/'),
  
  // Payment APIs
  initiatePayment: (data) => api.post('/payment/initiate/', data),
  getPaymentStatus: (orderId) => api.get(`/payment/status/${orderId}/`),
  
  // Seller APIs
  getSellerProducts: () => api.get('/seller/products/'),
  createSellerProduct: (data) => api.post('/seller/products/', data),
  updateSellerProduct: (id, data) => api.patch(`/seller/products/${id}/`, data),
  deleteSellerProduct: (id) => api.delete(`/seller/products/${id}/`),
  uploadProductImages: (data) => api.post('/seller/upload-image/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getSellerOrders: () => api.get('/seller/orders/'),
  
  // Voucher APIs
  purchaseVoucher: (data) => api.post('/vouchers/purchase/', data),
  getVouchers: () => api.get('/vouchers/'),
  
  // Auth APIs
  login: (data) => api.post('/login/', data),
  signup: (data) => api.post('/signup/', data),
  getProfile: () => api.get('/profile/'),
};

export default api;