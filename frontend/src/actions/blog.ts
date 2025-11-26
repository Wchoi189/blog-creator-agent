'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { apiGet, apiPost, apiPut } from '@/lib/api-server'

export async function getDrafts() {
  try {
    const data = await apiGet<{ drafts: any[] }>('/api/v1/blog')
    return { drafts: data.drafts || [] }
  } catch (error) {
    return { error: 'Failed to fetch drafts' }
  }
}

export async function getDraft(id: string) {
  try {
    const draft = await apiGet<any>(`/api/v1/blog/${id}`)
    return { draft }
  } catch (error) {
    return { error: 'Failed to fetch draft' }
  }
}

export async function generateBlog(formData: FormData) {
  try {
    const documentIds = formData.getAll('documentIds') as string[]
    const title = formData.get('title') as string
    const description = formData.get('description') as string

    if (!documentIds || documentIds.length === 0) {
      return { error: 'Please select at least one document' }
    }

    if (!title) {
      return { error: 'Please provide a title' }
    }

    const response = await apiPost<any>('/api/v1/blog/generate', {
      document_ids: documentIds,
      title,
      description: description || undefined,
    })

    revalidatePath('/dashboard/drafts')
    return { draft: response }
  } catch (error) {
    return { error: 'Failed to generate blog' }
  }
}

export async function updateDraft(id: string, formData: FormData) {
  try {
    const title = formData.get('title') as string
    const content = formData.get('content') as string
    const status = formData.get('status') as string

    const response = await apiPut<any>(`/api/v1/blog/${id}`, {
      title,
      content,
      status,
    })

    revalidatePath('/dashboard/drafts')
    revalidatePath(`/dashboard/editor/${id}`)
    return { draft: response }
  } catch (error) {
    return { error: 'Failed to update draft' }
  }
}

export async function publishDraft(id: string) {
  try {
    const response = await apiPut<any>(`/api/v1/blog/${id}`, {
      status: 'published',
    })

    revalidatePath('/dashboard/drafts')
    return { draft: response }
  } catch (error) {
    return { error: 'Failed to publish draft' }
  }
}
