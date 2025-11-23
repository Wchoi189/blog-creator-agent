'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { authAPI } from '@/lib/api';
import { Key, Plus, Trash2 } from 'lucide-react';

interface APIKeyInfo {
  id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  expires_at?: string;
  last_used_at?: string;
}

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [apiKeys, setApiKeys] = useState<APIKeyInfo[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyExpiry, setNewKeyExpiry] = useState('');
  const [createdKey, setCreatedKey] = useState('');

  useEffect(() => {
    fetchAPIKeys();
  }, []);

  const fetchAPIKeys = async () => {
    try {
      const response = await authAPI.listAPIKeys();
      setApiKeys(response.data);
    } catch (error) {
      console.error('Failed to fetch API keys:', error);
    }
  };

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) {
      alert('Please enter a key name');
      return;
    }

    try {
      const response = await authAPI.createAPIKey(
        newKeyName,
        newKeyExpiry ? parseInt(newKeyExpiry) : undefined
      );
      setCreatedKey(response.data.key);
      setNewKeyName('');
      setNewKeyExpiry('');
      fetchAPIKeys();
    } catch (error) {
      console.error('Failed to create API key:', error);
      alert('Failed to create API key');
    }
  };

  const handleDeleteKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key?')) {
      return;
    }

    try {
      await authAPI.revokeAPIKey(keyId);
      fetchAPIKeys();
    } catch (error) {
      console.error('Failed to revoke API key:', error);
      alert('Failed to revoke API key');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">Manage your account and API keys.</p>
      </div>

      {/* Profile Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Profile</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Full Name
            </label>
            <input
              type="text"
              value={user?.full_name || ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
            />
          </div>
        </div>
      </div>

      {/* API Keys Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">API Keys</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
          >
            <Plus className="w-4 h-4" />
            <span>Create API Key</span>
          </button>
        </div>

        {apiKeys.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No API keys yet</p>
        ) : (
          <div className="space-y-3">
            {apiKeys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <Key className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900">{key.name}</p>
                    <p className="text-sm text-gray-500">{key.key_prefix}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteKey(key.id)}
                  className="text-red-600 hover:text-red-800 transition"
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
            <h3 className="text-xl font-semibold mb-4">Create API Key</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Key Name
                </label>
                <input
                  type="text"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="e.g., Production API"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expires In (days, optional)
                </label>
                <input
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
                  API Key Created! Copy it now - it won't be shown again:
                </p>
                <code className="block p-2 bg-white border border-green-300 rounded text-sm break-all">
                  {createdKey}
                </code>
              </div>
            )}

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setCreatedKey('');
                  setNewKeyName('');
                  setNewKeyExpiry('');
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                {createdKey ? 'Close' : 'Cancel'}
              </button>
              {!createdKey && (
                <button
                  onClick={handleCreateKey}
                  disabled={!newKeyName.trim()}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
                >
                  Create
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
