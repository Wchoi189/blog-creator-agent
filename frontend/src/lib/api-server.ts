/**
 * Server-side API client for Next.js Server Components and Server Actions
 * Uses httpOnly cookies for authentication
 * DO NOT import this in Client Components - use Server Actions instead
 */

import { cookies } from 'next/headers'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

/**
 * Get authentication headers from httpOnly cookies
 */
async function getAuthHeaders(): Promise<HeadersInit> {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')
  
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token.value}` }),
  }
}

/**
 * GET request to API
 */
export async function apiGet<T>(
  endpoint: string,
  options?: {
    cache?: RequestCache
    revalidate?: number
    tags?: string[]
  }
): Promise<T> {
  const headers = await getAuthHeaders()
  
  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'GET',
    headers,
    cache: options?.cache || 'no-store',
    ...(options?.revalidate && { next: { revalidate: options.revalidate } }),
    ...(options?.tags && { next: { tags: options.tags } }),
  })
  
  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API Error (${res.status}): ${error || res.statusText}`)
  }
  
  return res.json()
}

/**
 * POST request to API
 */
export async function apiPost<T>(
  endpoint: string,
  data?: unknown
): Promise<T> {
  const headers = await getAuthHeaders()
  
  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: data ? JSON.stringify(data) : undefined,
    cache: 'no-store',
  })
  
  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API Error (${res.status}): ${error || res.statusText}`)
  }
  
  return res.json()
}

/**
 * POST request for file upload (multipart/form-data)
 */
export async function apiPostFormData<T>(
  endpoint: string,
  formData: FormData
): Promise<T> {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')
  
  const headers: HeadersInit = {}
  if (token) {
    headers.Authorization = `Bearer ${token.value}`
  }
  
  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
    cache: 'no-store',
  })
  
  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API Error (${res.status}): ${error || res.statusText}`)
  }
  
  return res.json()
}

/**
 * Upload a file to the API
 */
export async function apiUploadFile<T>(
  endpoint: string,
  file: File
): Promise<T> {
  const formData = new FormData()
  formData.append('file', file)
  return apiPostFormData<T>(endpoint, formData)
}

/**
 * PUT request to API
 */
export async function apiPut<T>(
  endpoint: string,
  data: unknown
): Promise<T> {
  const headers = await getAuthHeaders()
  
  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify(data),
    cache: 'no-store',
  })
  
  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API Error (${res.status}): ${error || res.statusText}`)
  }
  
  return res.json()
}

/**
 * DELETE request to API
 */
export async function apiDelete(endpoint: string): Promise<void> {
  const headers = await getAuthHeaders()
  
  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'DELETE',
    headers,
    cache: 'no-store',
  })
  
  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API Error (${res.status}): ${error || res.statusText}`)
  }
}

/**
 * Typed API clients for specific resources
 */

// Documents API
export const documentsServerAPI = {
  list: () => apiGet<{ documents: any[] }>('/api/v1/documents', { 
    revalidate: 60, 
    tags: ['documents'] 
  }),
  
  get: (docId: string) => apiGet<any>(`/api/v1/documents/${docId}`, { 
    revalidate: 300 
  }),
  
  search: (query: string, documentIds?: string[], topK: number = 5) =>
    apiPost<any>('/api/v1/documents/search', { 
      query, 
      document_ids: documentIds, 
      top_k: topK 
    }),
}

// Blog API
export const blogServerAPI = {
  list: () => apiGet<{ drafts: any[] } | any[]>('/api/v1/blog', { 
    revalidate: 60, 
    tags: ['blog'] 
  }),
  
  get: (draftId: string) => apiGet<any>(`/api/v1/blog/${draftId}`, { 
    revalidate: 60 
  }),
}

// Sessions API
export const sessionsServerAPI = {
  list: () => apiGet<{ sessions: any[] }>('/api/v1/sessions', { 
    revalidate: 300 
  }),
  
  get: (sessionId: string) => apiGet<any>(`/api/v1/sessions/${sessionId}`),
  
  getChatHistory: (sessionId: string) => 
    apiGet<any>(`/api/v1/sessions/${sessionId}/chat-history`),
}
