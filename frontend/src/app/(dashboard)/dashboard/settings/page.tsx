import { Metadata } from 'next'
import { getCurrentUser } from '@/actions/auth'
import SettingsClient from './settings-client'

export const metadata: Metadata = {
  title: 'Settings | Blog Creator',
  description: 'Manage your account settings',
}

/**
 * Settings Page - Server Component
 * Fetches user server-side
 */
export default async function SettingsPage() {
  const { user } = await getCurrentUser()
  
  return <SettingsClient user={user} />
}
