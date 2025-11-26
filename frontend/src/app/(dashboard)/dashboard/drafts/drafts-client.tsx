'use client'

import { useState } from 'react'
import Link from 'next/link'
import { FileText, Trash2, Edit, Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface Draft {
  id: string
  title: string
  status: string
  created_at: string
  updated_at: string
}

interface DraftsClientProps {
  drafts: Draft[]
}

/**
 * Drafts Client Component
 * Handles interactive features (delete confirmations, UI state)
 */
export default function DraftsClient({ drafts }: DraftsClientProps) {
  const router = useRouter()
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this draft?')) return
    
    setDeletingId(id)
    try {
      // Use Server Action import when available
      const response = await fetch(`/api/v1/blog/${id}`, {
        method: 'DELETE',
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete')
      }
      
      router.refresh()
    } catch (error) {
      console.error('Failed to delete draft:', error)
      alert('Failed to delete draft')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Blog Drafts</h1>
        <Link
          href="/dashboard/generate"
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <Plus className="w-5 h-5" aria-hidden="true" />
          <span>Generate New</span>
        </Link>
      </div>

      {drafts.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" aria-hidden="true" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No drafts yet</h3>
          <p className="text-gray-600 mb-6">Create your first blog draft to get started</p>
          <Link
            href="/dashboard/generate"
            className="inline-flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <Plus className="w-5 h-5" aria-hidden="true" />
            <span>Generate Draft</span>
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Title
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Updated
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {drafts.map((draft) => (
                <tr key={draft.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 text-gray-400 mr-3" aria-hidden="true" />
                      <span className="text-sm font-medium text-gray-900">{draft.title}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                      {draft.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(draft.updated_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-4">
                    <Link
                      href={`/dashboard/editor/${draft.id}`}
                      className="text-primary-600 hover:text-primary-900 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded inline-block"
                      aria-label={`Edit ${draft.title}`}
                    >
                      <Edit className="w-5 h-5" />
                    </Link>
                    <button
                      onClick={() => handleDelete(draft.id)}
                      disabled={deletingId === draft.id}
                      className="text-red-600 hover:text-red-900 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
                      aria-label={`Delete ${draft.title}`}
                    >
                      {deletingId === draft.id ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-red-600 inline-block" />
                      ) : (
                        <Trash2 className="w-5 h-5" />
                      )}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
