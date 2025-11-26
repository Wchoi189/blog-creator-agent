import { Metadata } from 'next'
import { blogServerAPI } from '@/lib/api-server'
import DraftsClient from './drafts-client'

export const metadata: Metadata = {
  title: 'Blog Drafts | Blog Creator',
  description: 'Manage your blog drafts',
}

/**
 * Drafts Page - Server Component
 * Fetches drafts server-side using httpOnly cookies
 */
export default async function DraftsPage() {
  // Fetch drafts from server-side using httpOnly cookies
  const data = await blogServerAPI.list()
  
  // Handle both array and object response formats
  const drafts = Array.isArray(data) ? data : (data as { drafts: any[] }).drafts || []
  
  return <DraftsClient drafts={drafts} />
}
