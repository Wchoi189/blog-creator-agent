'use server'

import { revalidatePath } from 'next/cache'
import { apiGet, apiPost, apiDelete, apiUploadFile } from '@/lib/api-server'

export async function getDocuments() {
  try {
    const data = await apiGet<{ documents: any[] }>('/api/v1/documents')
    return { documents: data.documents }
  } catch (error) {
    return { error: 'Failed to fetch documents' }
  }
}

export async function getDocument(id: string) {
  try {
    const document = await apiGet<any>(`/api/v1/documents/${id}`)
    return { document }
  } catch (error) {
    return { error: 'Failed to fetch document' }
  }
}

export async function uploadDocument(formData: FormData) {
  try {
    const file = formData.get('file') as File
    if (!file) {
      return { error: 'No file provided' }
    }

    const document = await apiUploadFile('/api/v1/documents/upload', file)
    
    revalidatePath('/dashboard/documents')
    return { document }
  } catch (error) {
    return { error: 'Failed to upload document' }
  }
}

export async function deleteDocument(id: string) {
  try {
    await apiDelete(`/api/v1/documents/${id}`)
    
    revalidatePath('/dashboard/documents')
    return { success: true }
  } catch (error) {
    return { error: 'Failed to delete document' }
  }
}
