/**
 * API client for backend communication
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add JWT token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: { email: string; password: string; full_name?: string }) =>
    api.post('/api/v1/auth/register', data),

  login: (email: string, password: string) =>
    api.post('/api/v1/auth/login', { email, password }),

  getCurrentUser: () =>
    api.get('/api/v1/auth/me'),

  createAPIKey: (name: string, expiresInDays?: number) =>
    api.post('/api/v1/auth/api-keys', { name, expires_in_days: expiresInDays }),

  listAPIKeys: () =>
    api.get('/api/v1/auth/api-keys'),

  revokeAPIKey: (keyId: string) =>
    api.delete(`/api/v1/auth/api-keys/${keyId}`),
};

// Documents API
export const documentsAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/v1/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  list: () =>
    api.get('/api/v1/documents'),

  get: (docId: string) =>
    api.get(`/api/v1/documents/${docId}`),

  delete: (docId: string) =>
    api.delete(`/api/v1/documents/${docId}`),

  process: (docId: string) =>
    api.post(`/api/v1/documents/${docId}/process`),

  search: (query: string, documentIds?: string[], topK: number = 5) =>
    api.post('/api/v1/documents/search', { query, document_ids: documentIds, top_k: topK }),
};

// Blog API
export const blogAPI = {
  generate: (data: {
    document_ids: string[];
    title?: string;
    instructions?: string;
    categories?: string[];
    tags?: string[];
    session_id: string;
  }) =>
    api.post('/api/v1/blog/generate', data, { params: { session_id: data.session_id } }),

  generateContent: (draftId: string, instructions?: string) =>
    api.post(`/api/v1/blog/${draftId}/generate-content`, { instructions }),

  refine: (draftId: string, feedback: string) =>
    api.post(`/api/v1/blog/${draftId}/refine`, { feedback }),

  list: () =>
    api.get('/api/v1/blog'),

  get: (draftId: string) =>
    api.get(`/api/v1/blog/${draftId}`),

  update: (draftId: string, data: {
    title?: string;
    content?: string;
    categories?: string[];
    tags?: string[];
  }) =>
    api.put(`/api/v1/blog/${draftId}`, data),

  delete: (draftId: string) =>
    api.delete(`/api/v1/blog/${draftId}`),

  export: (draftId: string, format: string = 'markdown') =>
    api.post(`/api/v1/blog/${draftId}/export`, { format }),
};

// Sessions API
export const sessionsAPI = {
  create: (data: {
    name?: string;
    llm_provider?: string;
    llm_model?: string;
  }) =>
    api.post('/api/v1/sessions', data),

  list: () =>
    api.get('/api/v1/sessions'),

  get: (sessionId: string) =>
    api.get(`/api/v1/sessions/${sessionId}`),

  delete: (sessionId: string) =>
    api.delete(`/api/v1/sessions/${sessionId}`),

  getChatHistory: (sessionId: string) =>
    api.get(`/api/v1/sessions/${sessionId}/chat-history`),
};

export default api;
