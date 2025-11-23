/**
 * TypeScript types for API responses
 */

export interface User {
  id: string;
  email: string;
  full_name?: string;
  created_at: string;
  is_active: boolean;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface APIKey {
  id: string;
  name: string;
  key?: string;
  key_prefix: string;
  created_at: string;
  expires_at?: string;
  last_used_at?: string;
}

export enum DocumentType {
  PDF = 'pdf',
  AUDIO = 'audio',
  IMAGE = 'image',
  MARKDOWN = 'markdown',
}

export enum ProcessingStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface Document {
  id: string;
  user_id: string;
  filename: string;
  file_type: DocumentType;
  file_path: string;
  size: number;
  status: ProcessingStatus;
  chunk_count?: number;
  created_at: string;
  processed_at?: string;
  error_message?: string;
}

export enum BlogStatus {
  DRAFT = 'draft',
  GENERATING = 'generating',
  COMPLETED = 'completed',
  PUBLISHED = 'published',
  FAILED = 'failed',
}

export interface BlogDraft {
  id: string;
  user_id: string;
  session_id: string;
  title: string;
  content: string;
  status: BlogStatus;
  version: number;
  document_ids: string[];
  categories: string[];
  tags: string[];
  created_at: string;
  updated_at: string;
  published_at?: string;
  published_url?: string;
}

export interface Session {
  id: string;
  user_id: string;
  name: string;
  llm_provider: string;
  llm_model: string;
  created_at: string;
  updated_at: string;
  document_ids: string[];
  draft_ids: string[];
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}
