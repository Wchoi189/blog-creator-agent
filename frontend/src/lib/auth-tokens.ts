'use server'

import { cookies } from 'next/headers'

interface AuthTokens {
  accessToken: string
  refreshToken?: string
}

/**
 * Set authentication cookies (httpOnly for security)
 * Called after successful login
 */
export async function setAuthCookies({ accessToken, refreshToken }: AuthTokens) {
  const cookieStore = await cookies()
  
  // Set access token cookie - also set a client-readable version for client-side API calls
  cookieStore.set('access_token', accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24, // 24 hours
  })
  
  // Set client-readable token for client-side API calls (needed for axios interceptor)
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
