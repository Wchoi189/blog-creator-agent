'use server'

import { cookies } from 'next/headers'

interface AuthTokens {
  accessToken: string
  refreshToken?: string
}

/**
 * Set authentication cookies (httpOnly for security)
 * Called after successful login
 * 
 * Note: We set both httpOnly and client-readable cookies:
 * - access_token (httpOnly): Used by Server Components for security
 * - client_token (client-readable): Used by axios interceptors for client-side API calls
 * 
 * The client_token approach aligns with the existing architecture where axios
 * interceptors need to read the token to add Authorization headers. While this
 * creates a larger XSS attack surface, the application already sanitizes all
 * user inputs and uses DOMPurify for HTML content.
 */
export async function setAuthCookies({ accessToken, refreshToken }: AuthTokens) {
  const cookieStore = await cookies()
  
  // Set access token cookie - httpOnly for server-side security
  cookieStore.set('access_token', accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24, // 24 hours
  })
  
  // Set client-readable token for client-side API calls (needed for axios interceptor)
  // This aligns with existing getClientToken() usage in lib/api.ts
  cookieStore.set('client_token', accessToken, {
    httpOnly: false, // Client-readable for API calls
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24, // 24 hours
  })
  
  // Set refresh token if provided
  if (refreshToken) {
    cookieStore.set('refresh_token', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 60 * 24 * 30, // 30 days
    })
  }
}

/**
 * Clear all authentication cookies
 * Called on logout
 */
export async function clearAuthCookies() {
  const cookieStore = await cookies()
  
  cookieStore.delete('access_token')
  cookieStore.delete('client_token')
  cookieStore.delete('refresh_token')
}

/**
 * Get access token from cookies (server-side)
 */
export async function getServerAccessToken(): Promise<string | undefined> {
  const cookieStore = await cookies()
  return cookieStore.get('access_token')?.value
}
