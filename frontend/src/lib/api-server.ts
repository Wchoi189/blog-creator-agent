/**
 * Server-side API client for Next.js Server Components and Server Actions
 * Uses httpOnly cookies for authentication
 * DO NOT import this in Client Components - use Server Actions instead
 */

import { cookies } from 'next/headers'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

type GetOptions = {
  cache?: RequestCache
  revalidate?: number
  tags?: string[]
}

async function getAuthHeaders(options?: { json?: boolean }): Promise<HeadersInit> {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')

  const headers: HeadersInit = {}
  if (options?.json) {
    headers['Content-Type'] = 'application/json'
  }
  if (token) {
    headers.Authorization = `Bearer ${token.value}`
  }

  return headers
}

function buildGetInit(
  headers: HeadersInit,
  options?: GetOptions,
): RequestInit & { next?: { revalidate?: number; tags?: string[] } } {
  const init: RequestInit & { next?: { revalidate?: number; tags?: string[] } } = {
    method: 'GET',
    headers,
  }

  if (options?.cache && options?.revalidate === undefined) {
    init.cache = options.cache
  } else if (!options?.revalidate) {
    init.cache = 'no-store'
  }

  if (options?.revalidate !== undefined || options?.tags) {
    init.next = {}
    if (options?.revalidate !== undefined) {
      init.next.revalidate = options.revalidate
    }
    if (options?.tags) {
      init.next.tags = options.tags
    }
  }

  return init
}

export async function apiGet<T>(endpoint: string, options?: GetOptions): Promise<T> {
  const res = await fetch(
    `${API_URL}${endpoint}`,
    buildGetInit(await getAuthHeaders({ json: true }), options),
  )

  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API Error (${res.status}): ${error || res.statusText}`)
  }

  return res.json()
}

export async function apiPost<T>(endpoint: string, data?: unknown): Promise<T> {
  const payload = data ? JSON.stringify(data) : undefined
  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: await getAuthHeaders({ json: true }),
    body: payload,
    cache: 'no-store',
  })

  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API Error (${res.status}): ${error || res.statusText}`)
  }

  return res.json()
}

export async function apiPostFormData<T>(endpoint: string, formData: FormData): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: formData,
    cache: 'no-store',
  })

  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API Error (${res.status}): ${error || res.statusText}`)
  }

  return res.json()
}

export async function apiUploadFile<T>(endpoint: string, file: File): Promise<T> {
  const formData = new FormData()
  formData.append('file', file)
  return apiPostFormData<T>(endpoint, formData)
}

export async function apiPut<T>(endpoint: string, data: unknown): Promise<T> {
  const payload = JSON.stringify(data)
  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'PUT',
    headers: await getAuthHeaders({ json: true }),
    body: payload,
    cache: 'no-store',
  })

  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API Error (${res.status}): ${error || res.statusText}`)
  }

  return res.json()
}

export async function apiDelete(endpoint: string): Promise<void> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'DELETE',
    headers: await getAuthHeaders({ json: true }),
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
