import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const fetchPopularRecommendations = async (limit = 10) => {
  const response = await api.get(`/recommendations/popular?limit=${limit}`);
  return response.data;
};

export const fetchCollaborativeRecommendations = async (userId, limit = 10) => {
  const response = await api.get(`/recommendations/user/${userId}?limit=${limit}`);
  return response.data;
};

export const fetchHybridRecommendations = async (userId, limit = 10, cfWeight = null, popWeight = null) => {
  let url = `/recommendations/hybrid/${userId}?limit=${limit}`;
  if (cfWeight !== null && popWeight !== null) {
    url += `&cf_weight=${cfWeight}&popularity_weight=${popWeight}`;
  }
  const response = await api.get(url);
  return response.data;
};

export const searchBooks = async (q, limit = 20) => {
  const response = await api.get(`/books/search?q=${encodeURIComponent(q)}&limit=${limit}`);
  return response.data;
};

export const fetchBookDetails = async (isbn) => {
  const response = await api.get(`/books/${encodeURIComponent(isbn)}`);
  return response.data;
};

export const fetchSimilarBooks = async (isbn, limit = 6) => {
  const response = await api.get(`/books/${encodeURIComponent(isbn)}/similar?limit=${limit}`);
  return response.data;
};

export const submitRating = async (userId, isbn, rating) => {
  const response = await api.post('/ratings', {
    user_id: parseInt(userId, 10),
    isbn: String(isbn),
    rating: parseInt(rating, 10),
  });
  return response.data;
};

export const fetchDemoUsers = async () => {
  const response = await api.get('/users/demo');
  return response.data;
};

export const fetchUserProfile = async (userId) => {
  const response = await api.get(`/users/${userId}`);
  return response.data;
};

export default api;
