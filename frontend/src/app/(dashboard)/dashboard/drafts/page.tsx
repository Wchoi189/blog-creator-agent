'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { blogAPI } from '@/lib/api';
import { FileText, Trash2, Edit, Plus } from 'lucide-react';

interface Draft {
  id: string;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export default function DraftsPage() {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDrafts();
  }, []);

  const fetchDrafts = async () => {
    try {
      const res = await blogAPI.list();
      setDrafts(res.data);
    } catch (error) {
      console.error('Failed to fetch drafts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this draft?')) return;
    try {
      await blogAPI.delete(id);
      setDrafts(drafts.filter(d => d.id !== id));
    } catch (error) {
      console.error('Failed to delete draft:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Blog Drafts</h1>
        <Link
          href="/dashboard/generate"
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus className="w-5 h-5" />
          <span>Generate New</span>
        </Link>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : drafts.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No drafts yet</h3>
          <p className="text-gray-600 mb-6">Create your first blog draft to get started</p>
          <Link
            href="/dashboard/generate"
            className="inline-flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Plus className="w-5 h-5" />
            <span>Generate Draft</span>
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {drafts.map((draft) => (
                <tr key={draft.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 text-gray-400 mr-3" />
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
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link
                      href={`/dashboard/editor/${draft.id}`}
                      className="text-primary-600 hover:text-primary-900 mr-4"
                    >
                      <Edit className="w-5 h-5 inline" />
                    </Link>
                    <button
                      onClick={() => handleDelete(draft.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 className="w-5 h-5 inline" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
