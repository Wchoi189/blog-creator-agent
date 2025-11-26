'use client';

import { useEffect, useState } from 'react';
import { documentsAPI } from '@/lib/api';
import { Document, ProcessingStatus } from '@/types/api';
import { FileText, Image, Music, Trash2, CheckCircle, Clock, XCircle } from 'lucide-react';
import Link from 'next/link';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await documentsAPI.list();
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await documentsAPI.delete(docId);
      setDocuments((prev) => prev.filter((doc) => doc.id !== docId));
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert('Failed to delete document');
    }
  };

  const getFileIcon = (type: string) => {
    if (type === 'image') {
      return <Image className="w-6 h-6 text-blue-500" />;
    } else if (type === 'audio') {
      return <Music className="w-6 h-6 text-purple-500" />;
    } else {
      return <FileText className="w-6 h-6 text-green-500" />;
    }
  };

  const getStatusBadge = (status: ProcessingStatus) => {
    switch (status) {
      case ProcessingStatus.COMPLETED:
        return (
          <span className="flex items-center space-x-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
            <CheckCircle className="w-3 h-3" />
            <span>Completed</span>
          </span>
        );
      case ProcessingStatus.PROCESSING:
        return (
          <span className="flex items-center space-x-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
            <Clock className="w-3 h-3" />
            <span>Processing</span>
          </span>
        );
      case ProcessingStatus.FAILED:
        return (
          <span className="flex items-center space-x-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
            <XCircle className="w-3 h-3" />
            <span>Failed</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center space-x-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
            <Clock className="w-3 h-3" />
            <span>Pending</span>
          </span>
        );
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
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
          className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
        >
          Upload Documents
        </Link>
      </div>

      {documents.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FileText className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
          <p className="text-gray-600 mb-6">
            Upload your first document to get started with AI-powered blog generation.
          </p>
          <Link
            href="/dashboard/upload"
            className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
          >
            Upload Documents
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Chunks
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documents.map((doc) => (
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
                  <td className="px-6 py-4">
                    {getStatusBadge(doc.status)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {doc.chunk_count || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="text-red-600 hover:text-red-800 transition"
                    >
                      <Trash2 className="w-5 h-5" />
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
