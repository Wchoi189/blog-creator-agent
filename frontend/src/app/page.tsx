export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-4">Blog Creator</h1>
        <p className="text-lg mb-8">
          AI-powered blog content generation with RAG capabilities
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Features</h2>
            <ul className="list-disc list-inside space-y-2">
              <li>Document upload (PDF, audio, images)</li>
              <li>RAG-based content generation</li>
              <li>Real-time collaborative editing</li>
              <li>GitHub Pages publishing</li>
            </ul>
          </div>

          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Quick Start</h2>
            <ol className="list-decimal list-inside space-y-2">
              <li>Upload your documents</li>
              <li>Generate blog draft</li>
              <li>Refine with AI assistant</li>
              <li>Publish to GitHub</li>
            </ol>
          </div>
        </div>
      </div>
    </main>
  )
}
