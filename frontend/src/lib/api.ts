/**
 * API client for backend communication (Client-side)
 * 
 * WARNING: This file is being phased out in favor of:
 * - Server Actions for mutations
 * - api-server.ts for Server Component data fetching
 * 
 * Only keep this for:
 * 1. Editor page (complex client-side operations)
 * 2. Settings page (API key management)
 * 
 * Authentication: Relies on httpOnly cookies sent automatically by browser
 * NO localStorage usage for tokens
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with credentials to send cookies
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important: Send cookies with requests
});

function getClientToken(): string | undefined {
  if (typeof document === 'undefined') {
    return undefined;
  }

  const match = document.cookie
    .split(';')
    .map((cookie) => cookie.trim())
    .find((cookie) => cookie.startsWith('client_token='));

  if (!match) {
    return undefined;
  }

  return decodeURIComponent(match.split('=')[1]);
}

api.interceptors.request.use((config) => {
  const token = getClientToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Redirect to login on auth error
      // Cookies will be cleared by the server or middleware
      if (typeof window !== 'undefined') {
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
      headers: { 'Content-Type': undefined },
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
