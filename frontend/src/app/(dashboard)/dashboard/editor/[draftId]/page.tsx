'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { blogAPI } from '@/lib/api';
import { BlogDraft } from '@/types/api';
import TiptapEditor from '@/components/editor/TiptapEditor';
import { Save, Download, ArrowLeft, Sparkles } from 'lucide-react';

export default function EditorPage() {
  const params = useParams();
  const router = useRouter();
  const draftId = params.draftId as string;

  const [draft, setDraft] = useState<BlogDraft | null>(null);
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [refining, setRefining] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);

  useEffect(() => {
    fetchDraft();
  }, [draftId]);

  const fetchDraft = async () => {
    try {
      const response = await blogAPI.get(draftId);
      const draftData = response.data;
      setDraft(draftData);
      setContent(draftData.content);
      setTitle(draftData.title);
    } catch (error) {
      console.error('Failed to fetch draft:', error);
      alert('Failed to load draft');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await blogAPI.update(draftId, { title, content });
      alert('Draft saved successfully!');
    } catch (error) {
      console.error('Failed to save draft:', error);
      alert('Failed to save draft');
    } finally {
      setSaving(false);
    }
  };

  const handleRefine = async () => {
    if (!feedback.trim()) {
      alert('Please provide feedback for refinement');
      return;
    }

    setRefining(true);
    setShowFeedbackModal(false);

    try {
      const response = await blogAPI.refine(draftId, feedback);
      // In a real implementation, we'd handle streaming here
      // For now, just refresh the draft
      await fetchDraft();
      setFeedback('');
      alert('Draft refined successfully!');
    } catch (error) {
      console.error('Failed to refine draft:', error);
      alert('Failed to refine draft');
    } finally {
      setRefining(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await blogAPI.export(draftId);
      const blob = new Blob([response.data], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title.toLowerCase().replace(/\s+/g, '-')}.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to export draft:', error);
      alert('Failed to export draft');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!draft) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Draft not found</p>
        <button
          onClick={() => router.push('/dashboard')}
          className="mt-4 text-primary-600 hover:text-primary-700"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => router.push('/dashboard')}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </button>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowFeedbackModal(true)}
            disabled={refining}
            className="flex items-center space-x-2 px-4 py-2 border border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50 transition disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            <span>Refine with AI</span>
          </button>
          <button
            onClick={handleExport}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save'}</span>
          </button>
        </div>
      </div>

      {/* Title Input */}
      <div>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full text-3xl font-bold border-none focus:outline-none focus:ring-0 px-0"
          placeholder="Blog Post Title"
        />
      </div>

      {/* Editor */}
      <TiptapEditor content={content} onChange={setContent} />

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
            <h3 className="text-xl font-semibold mb-4">Refine with AI</h3>
            <p className="text-gray-600 mb-4">
              Provide feedback on how you'd like to improve the draft:
            </p>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              className="w-full border border-gray-300 rounded-lg p-3 min-h-[120px] focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., Make it more concise, add more examples, improve the introduction..."
            />
            <div className="flex justify-end space-x-3 mt-4">
              <button
                onClick={() => setShowFeedbackModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleRefine}
                disabled={!feedback.trim()}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
              >
                Refine
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
