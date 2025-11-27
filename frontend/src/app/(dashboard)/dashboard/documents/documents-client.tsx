'use client'

import { useState } from 'react'
import { Document, ProcessingStatus } from '@/types/api'
import { FileText, Image, Music, Trash2, CheckCircle, Clock, XCircle } from 'lucide-react'
import Link from 'next/link'
import { deleteDocument } from '@/actions/documents'
import { useRouter } from 'next/navigation'

interface DocumentsClientProps {
  documents: Document[]
}

/**
 * Documents Client Component
 * Handles interactive features (delete confirmations, UI state)
 */
export default function DocumentsClient({ documents: initialDocuments }: DocumentsClientProps) {
  const router = useRouter()
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return
    }

    setDeletingId(docId)
    try {
      const result = await deleteDocument(docId)
      if (result.error) {
        alert(`Failed to delete document: ${result.error}`)
      } else {
        // Router will refresh and fetch updated data
        router.refresh()
      }
    } catch (error) {
      console.error('Failed to delete document:', error)
      alert('Failed to delete document')
    } finally {
      setDeletingId(null)
    }
  }

  const getFileIcon = (type: string) => {
    if (type === 'image') {
      return <Image className="w-6 h-6 text-blue-500" aria-hidden="true" />
    } else if (type === 'audio') {
      return <Music className="w-6 h-6 text-purple-500" aria-hidden="true" />
    } else {
      return <FileText className="w-6 h-6 text-green-500" aria-hidden="true" />
    }
  }

  const getStatusBadge = (status: ProcessingStatus) => {
    switch (status) {
      case ProcessingStatus.COMPLETED:
        return (
          <span className="flex items-center space-x-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
            <CheckCircle className="w-3 h-3" aria-hidden="true" />
            <span>Completed</span>
          </span>
        )
      case ProcessingStatus.PROCESSING:
        return (
          <span className="flex items-center space-x-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
            <Clock className="w-3 h-3" aria-hidden="true" />
            <span>Processing</span>
          </span>
        )
      case ProcessingStatus.FAILED:
        return (
          <span className="flex items-center space-x-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
            <XCircle className="w-3 h-3" aria-hidden="true" />
            <span>Failed</span>
          </span>
        )
      default:
        return (
          <span className="flex items-center space-x-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
            <Clock className="w-3 h-3" aria-hidden="true" />
            <span>Pending</span>
          </span>
        )
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <p className="mt-2 text-gray-600">
            Manage your uploaded documents and their processing status.
          </p>
        </div>
        <Link
          href="/dashboard/upload"
          className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          Upload Documents
        </Link>
      </div>

      {initialDocuments.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FileText className="w-16 h-16 mx-auto text-gray-400 mb-4" aria-hidden="true" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
          <p className="text-gray-600 mb-6">
            Upload your first document to get started with AI-powered blog generation.
          </p>
          <Link
            href="/dashboard/upload"
            className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            Upload Documents
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Chunks
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {initialDocuments.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      {getFileIcon(doc.file_type)}
                      <div>
                        <p className="font-medium text-gray-900">{doc.filename}</p>
                        <p className="text-sm text-gray-500">
                          {(doc.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 capitalize">
                    {doc.file_type}
                  </td>
                  <td className="px-6 py-4">{getStatusBadge(doc.status)}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {doc.chunk_count || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(doc.id)}
                      disabled={deletingId === doc.id}
                      className="text-red-600 hover:text-red-800 transition disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
                      aria-label={`Delete ${doc.filename}`}
                    >
                      {deletingId === doc.id ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-red-600" />
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
