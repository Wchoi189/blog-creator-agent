'use client'

import { useState, useEffect } from 'react'
import { authAPI } from '@/lib/api'
import { Key, Plus, Trash2 } from 'lucide-react'

interface APIKeyInfo {
  id: string
  name: string
  key_prefix: string
  created_at: string
  expires_at?: string
  last_used_at?: string
}

interface SettingsClientProps {
  user: any
}

/**
 * Settings Client Component
 * Manages API keys and account settings
 */
export default function SettingsClient({ user }: SettingsClientProps) {
  const [apiKeys, setApiKeys] = useState<APIKeyInfo[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyExpiry, setNewKeyExpiry] = useState('')
  const [createdKey, setCreatedKey] = useState('')

  useEffect(() => {
    fetchAPIKeys()
  }, [])

  const fetchAPIKeys = async () => {
    try {
      const response = await authAPI.listAPIKeys()
      setApiKeys(response.data)
    } catch (error) {
      console.error('Failed to fetch API keys:', error)
    }
  }

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) {
      alert('Please enter a key name')
      return
    }

    try {
      const response = await authAPI.createAPIKey(
        newKeyName,
        newKeyExpiry ? parseInt(newKeyExpiry) : undefined
      )
      setCreatedKey(response.data.key)
      setNewKeyName('')
      setNewKeyExpiry('')
      fetchAPIKeys()
    } catch (error) {
      console.error('Failed to create API key:', error)
      alert('Failed to create API key')
    }
  }

  const handleDeleteKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key?')) {
      return
    }

    try {
      await authAPI.revokeAPIKey(keyId)
      fetchAPIKeys()
    } catch (error) {
      console.error('Failed to revoke API key:', error)
      alert('Failed to revoke API key')
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">Manage your account and API keys.</p>
      </div>

      {/* Profile Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Profile</h2>
        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium text-gray-500">Email</label>
            <p className="text-gray-900">{user?.email}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Name</label>
            <p className="text-gray-900">{user?.full_name || 'Not set'}</p>
          </div>
        </div>
      </div>

      {/* API Keys Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">API Keys</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <Plus className="w-4 h-4" aria-hidden="true" />
            <span>Create API Key</span>
          </button>
        </div>

        {apiKeys.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Key className="w-12 h-12 mx-auto mb-2 text-gray-400" aria-hidden="true" />
            <p>No API keys yet</p>
            <p className="text-sm">Create your first API key to get started</p>
          </div>
        ) : (
          <div className="space-y-4">
            {apiKeys.map((key) => (
              <div key={key.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <Key className="w-4 h-4 text-gray-400" aria-hidden="true" />
                    <span className="font-medium text-gray-900">{key.name}</span>
                  </div>
                  <div className="mt-1 space-y-1 text-sm text-gray-500">
                    <p>Key: {key.key_prefix}...</p>
                    <p>Created: {new Date(key.created_at).toLocaleDateString()}</p>
                    {key.expires_at && (
                      <p>Expires: {new Date(key.expires_at).toLocaleDateString()}</p>
                    )}
                    {key.last_used_at && (
                      <p>Last used: {new Date(key.last_used_at).toLocaleDateString()}</p>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteKey(key.id)}
                  className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded focus:outline-none focus:ring-2 focus:ring-red-500"
                  aria-label={`Delete ${key.name}`}
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create API Key Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Create API Key</h3>

            <div className="space-y-4">
              <div>
                <label htmlFor="key-name" className="block text-sm font-medium text-gray-700 mb-1">
                  Key Name
                </label>
                <input
                  id="key-name"
                  type="text"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="e.g., Production API"
                />
              </div>
              <div>
                <label htmlFor="key-expiry" className="block text-sm font-medium text-gray-700 mb-1">
                  Expires In (days, optional)
                </label>
                <input
                  id="key-expiry"
                  type="number"
                  value={newKeyExpiry}
                  onChange={(e) => setNewKeyExpiry(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Leave empty for no expiration"
                />
              </div>
            </div>

            {createdKey && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm font-medium text-green-800 mb-2">
                  API Key Created! Copy it now - it won&apos;t be shown again:
                </p>
                <code className="block p-2 bg-white border border-green-300 rounded text-sm break-all">
                  {createdKey}
                </code>
              </div>
            )}

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setCreatedKey('')
                  setNewKeyName('')
                  setNewKeyExpiry('')
                }}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-300"
              >
                Close
              </button>
              {!createdKey && (
                <button
                  onClick={handleCreateKey}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  Create
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
