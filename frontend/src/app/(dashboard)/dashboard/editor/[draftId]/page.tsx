'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { blogAPI, getClientToken } from '@/lib/api';
import { BlogDraft } from '@/types/api';
import TiptapEditor from '@/components/editor/TiptapEditor';
import { Save, Download, ArrowLeft, Sparkles } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

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
    let pollInterval: NodeJS.Timeout | null = null;

    const fetchDraft = async () => {
      try {
        const response = await blogAPI.get(draftId);
        const draftData = response.data;
        setDraft(draftData);
        setTitle(draftData.title);

        // If content is ready, set it and stop polling
        if (draftData.content && draftData.status !== 'generating') {
          setContent(draftData.content);
          setLoading(false);
          if (pollInterval) clearInterval(pollInterval);
        } else if (draftData.status === 'generating' || draftData.status === 'draft') {
          // Content still generating - keep polling
          if (!pollInterval) {
            pollInterval = setInterval(fetchDraft, 2000); // Poll every 2s
          }
        } else {
          // Failed or other status
          setContent(draftData.content || '');
          setLoading(false);
          if (pollInterval) clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Failed to fetch draft:', error);
        alert('Failed to load draft');
        setLoading(false);
        if (pollInterval) clearInterval(pollInterval);
      }
    };

    fetchDraft();

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [draftId]);

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
    console.log('handleRefine called, feedback:', feedback);
    
    if (!feedback.trim()) {
      alert('Please provide feedback for refinement');
      return;
    }

    // Prevent double-submission
    if (refining) {
      console.log('Already refining, returning');
      return;
    }

    setRefining(true);
    setShowFeedbackModal(false);
    console.log('Starting refine...');

    try {
      // Use fetch with streaming, adding Authorization header for auth
      const token = getClientToken();
      const response = await fetch(`${API_URL}/api/v1/blog/${draftId}/refine`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        credentials: 'include', // Send cookies for auth
        body: JSON.stringify({ feedback }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      // Read streaming response
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let streamedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        streamedContent += chunk;
        setContent(streamedContent);
      }

      setRefining(false);
      setFeedback('');
    } catch (error) {
      console.error('Failed to refine draft:', error);
      alert(error instanceof Error ? error.message : 'Failed to refine draft');
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
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        {draft?.status === 'generating' && (
          <p className="text-gray-600">Generating blog content with AI...</p>
        )}
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
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
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
          className="w-full text-3xl font-bold text-gray-900 border-none focus:outline-none focus:ring-0 px-0 placeholder:text-gray-400"
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
              Provide feedback on how you&apos;d like to improve the draft:
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
