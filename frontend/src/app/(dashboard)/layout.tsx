import { redirect } from 'next/navigation'
import { getCurrentUser } from '@/actions/auth'
import Navbar from '@/components/layout/Navbar'
import Sidebar from '@/components/layout/Sidebar'

/**
 * Dashboard Layout - Server Component
 * Fetches user from httpOnly cookies server-side
 * Middleware should already redirect unauthenticated users, but we double-check here
 */
export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Get user from httpOnly cookies (server-side)
  const { user } = await getCurrentUser()
  
  // If no user, redirect to login
  // Middleware should catch this, but this is a safeguard
  if (!user) {
    redirect('/login')
    return // Explicit return for clarity (redirect throws internally)
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6 ml-64 mt-16">
          {children}
        </main>
      </div>
    </div>
  )
}
