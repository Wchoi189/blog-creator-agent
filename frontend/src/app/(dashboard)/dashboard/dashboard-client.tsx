'use client'

import Link from 'next/link'
import { FileText, Upload, FileCheck, TrendingUp } from 'lucide-react'

interface DashboardClientProps {
  user: any
  stats: {
    documents: number
    drafts: number
    sessions: number
  }
}

interface StatCardProps {
  title: string
  value: number
  icon: React.ComponentType<{ className?: string }>
  color: 'blue' | 'green' | 'purple'
}

/**
 * Dashboard Client Component
 * Displays dashboard UI with stats and quick actions
 */
export default function DashboardClient({ user, stats }: DashboardClientProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.full_name || 'there'}!
        </h1>
        <p className="mt-2 text-gray-600">
          Here&apos;s an overview of your blog creation progress.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Documents" value={stats.documents} icon={FileText} color="blue" />
        <StatCard title="Blog Drafts" value={stats.drafts} icon={FileCheck} color="green" />
        <StatCard title="Sessions" value={stats.sessions} icon={TrendingUp} color="purple" />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/dashboard/upload"
            className="flex items-center space-x-3 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <Upload className="w-8 h-8 text-primary-600" aria-hidden="true" />
            <div>
              <h3 className="font-medium text-gray-900">Upload Documents</h3>
              <p className="text-sm text-gray-500">Upload PDF, audio, or images</p>
            </div>
          </Link>

          <Link
            href="/dashboard/documents"
            className="flex items-center space-x-3 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <FileText className="w-8 h-8 text-primary-600" aria-hidden="true" />
            <div>
              <h3 className="font-medium text-gray-900">View Documents</h3>
              <p className="text-sm text-gray-500">Manage your uploaded files</p>
            </div>
          </Link>
        </div>
      </div>

      {/* Getting Started */}
      <div className="bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Getting Started</h2>
        <p className="text-gray-700 mb-4">
          Follow these steps to create your first AI-powered blog post:
        </p>
        <ol className="space-y-2 text-gray-700">
          <li className="flex items-start space-x-2">
            <span className="font-semibold text-primary-700">1.</span>
            <span>Upload your source documents (PDF, audio, or images)</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="font-semibold text-primary-700">2.</span>
            <span>Wait for documents to be processed and vectorized</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="font-semibold text-primary-700">3.</span>
            <span>Generate a blog draft using AI</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="font-semibold text-primary-700">4.</span>
            <span>Refine the draft with AI assistance</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="font-semibold text-primary-700">5.</span>
            <span>Publish to GitHub Pages</span>
          </li>
        </ol>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon: Icon, color }: StatCardProps) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colors[color]}`}>
          <Icon className="w-6 h-6" aria-hidden="true" />
        </div>
      </div>
    </div>
  )
}
