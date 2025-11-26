import { Metadata } from 'next'
import { documentsServerAPI } from '@/lib/api-server'
import DocumentsClient from './documents-client'

export const metadata: Metadata = {
  title: 'Documents | Blog Creator',
  description: 'Manage your uploaded documents',
}

/**
 * Documents Page - Server Component
 * Fetches documents server-side using httpOnly cookies
 */
export default async function DocumentsPage() {
  // Fetch documents from server-side using httpOnly cookies
  const documents = await documentsServerAPI.list()
  
  return <DocumentsClient documents={documents.documents || []} />
}


