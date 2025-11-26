'use client'

import Link from 'next/link'
import { User, LogOut } from 'lucide-react'
import { useState } from 'react'
import { logout } from '@/actions/auth'

interface NavbarProps {
  user: {
    id: string
    email: string
    full_name?: string
  }
}

/**
 * Navbar Component - Client Component
 * Receives user as prop from Server Component layout
 * Uses Server Action for logout
 */
export default function Navbar({ user }: NavbarProps) {
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 fixed w-full z-10">
      <div className="px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">B</span>
            </div>
            <span className="text-xl font-semibold text-gray-900">Blog Creator</span>
          </Link>
        </div>

        <div className="flex items-center space-x-4">
          {/* User menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition"
              aria-label="User menu"
              aria-expanded={showUserMenu}
            >
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-primary-600" aria-hidden="true" />
              </div>
              <span className="text-sm font-medium text-gray-700">
                {user.full_name || user.email}
              </span>
            </button>

            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                <div className="px-4 py-2 border-b border-gray-100">
                  {user.full_name && (
                    <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
                  )}
                  <p className="text-xs text-gray-500">{user.email}</p>
                </div>
                <button
                  onClick={() => {
                    handleLogout()
                    setShowUserMenu(false)
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                >
                  <LogOut className="w-4 h-4" aria-hidden="true" />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
