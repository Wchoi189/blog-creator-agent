'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { documentsAPI, blogAPI, sessionsAPI } from '@/lib/api';
import { FileText, Sparkles } from 'lucide-react';

interface Document {
  id: string;
  filename: string;
  status: string;
}

export default function GeneratePage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [title, setTitle] = useState('');
  const [instructions, setInstructions] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await documentsAPI.list();
      setDocuments(res.data.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

  const toggleDoc = (id: string) => {
    setSelectedDocs(prev =>
      prev.includes(id) ? prev.filter(d => d !== id) : [...prev, id]
    );
  };

  const handleGenerate = async () => {
    if (selectedDocs.length === 0) {
      alert('Select at least one document');
      return;
    }

    setLoading(true);
    try {
      const sessionRes = await sessionsAPI.create({ name: `Blog: ${title || 'Untitled'}` });
      const session_id = sessionRes.data.id;

      const res = await blogAPI.generate({
        document_ids: selectedDocs,
        title: title || undefined,
        instructions: instructions || undefined,
        session_id,
      });

      router.push(`/dashboard/editor/${res.data.id}`);
    } catch (error) {
      console.error('Failed to generate blog:', error);
      alert('Failed to generate blog');
    } finally {
      setLoading(false);
    }
  };

  const processedDocs = documents.filter(d => d.status === 'completed');

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Generate Blog Post</h1>

      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Blog Title (Optional)
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter a title or let AI suggest one"
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Instructions (Optional)
          </label>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="Add any specific instructions for the AI..."
            rows={4}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
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
                  />
                  <FileText className="w-5 h-5 text-gray-400" />
                  <span className="text-sm text-gray-900">{doc.filename}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading || selectedDocs.length === 0}
          className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Sparkles className="w-5 h-5" />
          <span>{loading ? 'Generating...' : 'Generate Blog Post'}</span>
        </button>
      </div>
    </div>
  );
}
