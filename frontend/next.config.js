/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8002',
  },
  // Image optimization configuration
  images: {
    // Allow images from common domains if needed
    remotePatterns: [],
    // Enable modern image formats
    formats: ['image/avif', 'image/webp'],
    // Disable if not using next/image optimization
    unoptimized: true, // Set to false when using proper image hosting
  },
  // Compiler optimizations
  compiler: {
    // Remove console.log in production
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
  },
  // Experimental features for better performance
  experimental: {
    // Enable optimized package imports
    optimizePackageImports: ['lucide-react', '@tiptap/react'],
  },
}

module.exports = nextConfig
