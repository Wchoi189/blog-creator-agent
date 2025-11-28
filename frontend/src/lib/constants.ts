/**
 * Application-wide constants
 */

// API Configuration
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8002';

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    ME: '/api/v1/auth/me',
    API_KEYS: '/api/v1/auth/api-keys',
  },
  DOCUMENTS: {
    LIST: '/api/v1/documents',
    UPLOAD: '/api/v1/documents/upload',
    GET: (id: string) => `/api/v1/documents/${id}`,
    DELETE: (id: string) => `/api/v1/documents/${id}`,
    PROCESS: (id: string) => `/api/v1/documents/${id}/process`,
    SEARCH: '/api/v1/documents/search',
  },
  BLOG: {
    LIST: '/api/v1/blog',
    GENERATE: '/api/v1/blog/generate',
    GET: (id: string) => `/api/v1/blog/${id}`,
    UPDATE: (id: string) => `/api/v1/blog/${id}`,
    DELETE: (id: string) => `/api/v1/blog/${id}`,
    REFINE: (id: string) => `/api/v1/blog/${id}/refine`,
    EXPORT: (id: string) => `/api/v1/blog/${id}/export`,
    GENERATE_CONTENT: (id: string) => `/api/v1/blog/${id}/generate-content`,
  },
  SESSIONS: {
    LIST: '/api/v1/sessions',
    CREATE: '/api/v1/sessions',
    GET: (id: string) => `/api/v1/sessions/${id}`,
    DELETE: (id: string) => `/api/v1/sessions/${id}`,
    CHAT_HISTORY: (id: string) => `/api/v1/sessions/${id}/chat-history`,
  },
} as const;

// UI Constants
export const SIDEBAR_WIDTH = 256; // 64 * 4 = 256px (ml-64 in Tailwind)
export const NAVBAR_HEIGHT = 64; // h-16 in Tailwind

// File Upload Limits
export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const ALLOWED_FILE_TYPES = {
  documents: [
    'application/pdf',
    'text/plain',
    'text/markdown',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ],
  images: ['image/png', 'image/jpeg', 'image/gif', 'image/webp'],
  audio: ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/webm'],
} as const;

// Cache Configuration (in seconds)
export const CACHE_TTL = {
  DOCUMENTS: 60,
  BLOG_DRAFTS: 60,
  SESSIONS: 300,
  USER_PROFILE: 600,
} as const;

// Routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  DOCUMENTS: '/dashboard/documents',
  DRAFTS: '/dashboard/drafts',
  UPLOAD: '/dashboard/upload',
  GENERATE: '/dashboard/generate',
  SETTINGS: '/dashboard/settings',
  EDITOR: (draftId: string) => `/dashboard/editor/${draftId}`,
} as const;

// Status Labels
export const STATUS_LABELS = {
  pending: 'Pending',
  processing: 'Processing',
  completed: 'Completed',
  failed: 'Failed',
  draft: 'Draft',
  generating: 'Generating',
  published: 'Published',
} as const;

// Default Values
export const DEFAULTS = {
  LLM_PROVIDER: 'openai',
  LLM_MODEL: 'gpt-4o-mini',
  SESSION_NAME: 'New Session',
  POLL_INTERVAL: 2000, // ms
  RECONNECT_DELAY: 3000, // ms
} as const;
