'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

type FormState = {
  error?: string
}

export async function login(prevState: FormState, formData: FormData): Promise<FormState> {
  const email = formData.get('email') as string
  const password = formData.get('password') as string
  
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    
    if (!response.ok) {
      return { error: 'Invalid credentials' }
    }
    
    const { access_token, refresh_token } = await response.json()
    
    const cookieStore = await cookies()
    cookieStore.set('access_token', access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/',
    })
    
    cookieStore.set('refresh_token', refresh_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 30, // 30 days
      path: '/',
    })
  } catch (error) {
    return { error: 'Login failed' }
  }
  
  redirect('/dashboard')
}

export async function register(prevState: FormState, formData: FormData): Promise<FormState> {
  const email = formData.get('email') as string
  const password = formData.get('password') as string
  const fullName = formData.get('fullName') as string
  
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: fullName }),
    })
    
    if (!response.ok) {
      const data = await response.json()
      return { error: data.detail || 'Registration failed' }
    }
    
    // Auto-login after registration
    return login(prevState, formData)
  } catch (error) {
    return { error: 'Registration failed' }
  }
}

export async function logout() {
  const cookieStore = await cookies()
  cookieStore.delete('access_token')
  cookieStore.delete('refresh_token')
  redirect('/login')
}

export async function getAccessToken() {
  const cookieStore = await cookies()
  return cookieStore.get('access_token')?.value
}
