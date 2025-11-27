import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'
const ACCESS_COOKIE_MAX_AGE = 60 * 60 * 24
const REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24 * 30
const isProduction = process.env.NODE_ENV === 'production'

export async function middleware(request: NextRequest) {
  const accessToken = request.cookies.get('access_token')?.value
  const refreshToken = request.cookies.get('refresh_token')?.value
  const { pathname } = request.nextUrl

  const publicRoutes = ['/login', '/register']
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route))
  const isProtectedRoute = pathname.startsWith('/dashboard')

  if (isProtectedRoute) {
    if (!accessToken && refreshToken) {
      const refreshed = await refreshSessionTokens(request, refreshToken)
      if (refreshed) {
        return refreshed
      }
    } else if (accessToken && isTokenExpired(accessToken) && refreshToken) {
      const refreshed = await refreshSessionTokens(request, refreshToken)
      if (refreshed) {
        return refreshed
      }
    }
  }

  if (!accessToken && !refreshToken && isProtectedRoute) {
    return redirectToLogin(request)
  }

  if (!accessToken && !isPublicRoute && isProtectedRoute) {
    return redirectToLogin(request)
  }

  if (accessToken && isPublicRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

function decodeJwt(token: string): { exp?: number } | null {
  try {
    const [, payload] = token.split('.')
    if (!payload) {
      return null
    }
    const decoded = base64UrlDecode(payload)
    return JSON.parse(decoded)
  } catch (error) {
    return null
  }
}

function base64UrlDecode(input: string): string {
  const normalized = input.replace(/-/g, '+').replace(/_/g, '/')
  const padding = (4 - (normalized.length % 4 || 0)) % 4
  const padded = normalized.padEnd(normalized.length + padding, '=')

  if (typeof atob === 'function') {
    return atob(padded)
  }

  if (typeof Buffer !== 'undefined') {
    return Buffer.from(padded, 'base64').toString('utf8')
  }

  throw new Error('No base64 decoder available')
}

function isTokenExpired(token: string): boolean {
  const payload = decodeJwt(token)
  if (!payload?.exp) {
    return true
  }
  const nowInSeconds = Math.floor(Date.now() / 1000)
  return payload.exp <= nowInSeconds + 30 // refresh 30s before actual expiry
}

async function refreshSessionTokens(
  request: NextRequest,
  refreshToken: string,
): Promise<NextResponse | null> {
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: 'no-store',
    })

    if (!response.ok) {
      return redirectToLogin(request)
    }

    const { access_token, refresh_token } = await response.json()
    const redirectResponse = NextResponse.redirect(new URL(request.url))
    setCookiesOnResponse(redirectResponse, access_token, refresh_token)
    return redirectResponse
  } catch (error) {
    return redirectToLogin(request)
  }
}

function setCookiesOnResponse(
  response: NextResponse,
  accessToken: string,
  refreshToken: string,
) {
  response.cookies.set('access_token', accessToken, {
    httpOnly: true,
    secure: isProduction,
    sameSite: 'lax',
    maxAge: ACCESS_COOKIE_MAX_AGE,
    path: '/',
  })

  response.cookies.set('client_token', accessToken, {
    httpOnly: false,
    secure: isProduction,
    sameSite: 'lax',
    maxAge: ACCESS_COOKIE_MAX_AGE,
    path: '/',
  })

  response.cookies.set('refresh_token', refreshToken, {
    httpOnly: true,
    secure: isProduction,
    sameSite: 'lax',
    maxAge: REFRESH_COOKIE_MAX_AGE,
    path: '/',
  })
}

function redirectToLogin(request: NextRequest): NextResponse {
  const response = NextResponse.redirect(new URL('/login', request.url))
  response.cookies.delete('access_token')
  response.cookies.delete('client_token')
  response.cookies.delete('refresh_token')
  return response
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
