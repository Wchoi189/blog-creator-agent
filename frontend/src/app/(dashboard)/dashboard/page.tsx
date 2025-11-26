import { Metadata } from 'next'
import { getCurrentUser } from '@/actions/auth'
import { documentsServerAPI, blogServerAPI, sessionsServerAPI } from '@/lib/api-server'
import DashboardClient from './dashboard-client'

export const metadata: Metadata = {
  title: 'Dashboard | Blog Creator',
  description: 'Your blog creation dashboard',
}

/**
 * Dashboard Page - Server Component
 * Fetches user and stats server-side using httpOnly cookies
 */
export default async function DashboardPage() {
  // Fetch user from httpOnly cookies
  const { user } = await getCurrentUser()
  
  // Fetch stats in parallel
  try {
    const [docsData, draftsData, sessionsData] = await Promise.all([
      documentsServerAPI.list(),
      blogServerAPI.list(),
      sessionsServerAPI.list(),
    ])

    const stats = {
      documents: docsData.documents?.length || 0,
      drafts: draftsData.drafts?.length || draftsData.length || 0,
      sessions: sessionsData.sessions?.length || 0,
    }

    return <DashboardClient user={user} stats={stats} />
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
    // Return dashboard with zero stats on error
    return <DashboardClient user={user} stats={{ documents: 0, drafts: 0, sessions: 0 }} />
  }
}


