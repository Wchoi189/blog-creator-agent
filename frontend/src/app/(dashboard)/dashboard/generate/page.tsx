import { Metadata } from 'next'
import { documentsServerAPI } from '@/lib/api-server'
import GenerateClient from './generate-client'

export const metadata: Metadata = {
  title: 'Generate Blog | Blog Creator',
  description: 'Generate a new blog draft',
}

/**
 * Generate Page - Server Component
 * Fetches documents server-side
 */
export default async function GeneratePage() {
  const data = await documentsServerAPI.list()
  const documents = data.documents || []
  
  return <GenerateClient documents={documents} />
}


