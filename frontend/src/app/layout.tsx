import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Blog Creator',
  description: 'AI-powered blog content generation with RAG',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  )
}
