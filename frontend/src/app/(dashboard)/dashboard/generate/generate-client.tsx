'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { FileText, Sparkles } from 'lucide-react'

interface Document {
  id: string
  filename: string
  status: string
}

interface GenerateClientProps {
  documents: Document[]
}

/**
 * Generate Client Component
 * Handles blog generation form and submission
 */
export default function GenerateClient({ documents }: GenerateClientProps) {
  const router = useRouter()
  const [selectedDocs, setSelectedDocs] = useState<string[]>([])
  const [title, setTitle] = useState('')
  const [instructions, setInstructions] = useState('')
  const [loading, setLoading] = useState(false)

  const toggleDoc = (id: string) => {
    setSelectedDocs(prev =>
      prev.includes(id) ? prev.filter(d => d !== id) : [...prev, id]
    )
  }

  const handleGenerate = async () => {
    if (selectedDocs.length === 0) {
      alert('Select at least one document')
      return
    }

    setLoading(true)
    try {
      // Create session first (client-side API call for now)
      const sessionRes = await fetch('/api/v1/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: `Blog: ${title || 'Untitled'}` }),
      })
      
      if (!sessionRes.ok) throw new Error('Failed to create session')
      const sessionData = await sessionRes.json()
      const session_id = sessionData.id

      // Generate blog draft
      const res = await fetch(`/api/v1/blog/generate?session_id=${session_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_ids: selectedDocs,
          title: title || undefined,
          instructions: instructions || undefined,
        }),
      })

      if (!res.ok) throw new Error('Failed to generate blog')
      const data = await res.json()

      router.push(`/dashboard/editor/${data.id}`)
    } catch (error) {
      console.error('Failed to generate blog:', error)
      alert('Failed to generate blog')
    } finally {
      setLoading(false)
    }
  }

  const processedDocs = documents.filter(d => d.status === 'completed')

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Generate Blog Post</h1>

      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        <div>
          <label htmlFor="blog-title" className="block text-sm font-medium text-gray-700 mb-2">
            Blog Title (Optional)
          </label>
          <input
            id="blog-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter a title or let AI suggest one"
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
          />
        </div>

        <div>
          <label htmlFor="instructions" className="block text-sm font-medium text-gray-700 mb-2">
            Instructions (Optional)
          </label>
          <textarea
            id="instructions"
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="Add any specific instructions for the AI..."
            rows={4}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Documents ({selectedDocs.length} selected)
          </label>
          {processedDocs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No processed documents available. Upload and process documents first.
            </div>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto border rounded-lg p-4">
              {processedDocs.map((doc) => (
                <label
                  key={doc.id}
                  className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedDocs.includes(doc.id)}
                    onChange={() => toggleDoc(doc.id)}
                    className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                    aria-label={`Select ${doc.filename}`}
                  />
                  <FileText className="w-5 h-5 text-gray-400" aria-hidden="true" />
                  <span className="text-sm text-gray-900">{doc.filename}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading || selectedDocs.length === 0}
          className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <Sparkles className="w-5 h-5" aria-hidden="true" />
          <span>{loading ? 'Generating...' : 'Generate Blog Post'}</span>
        </button>
      </div>
    </div>
  )
}
