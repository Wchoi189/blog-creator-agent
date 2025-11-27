# Quick Reference Guide - Next.js Audit

**For:** Development Team  
**Purpose:** Quick lookup of common issues and fixes

---

## 🚨 Top 10 Critical Issues

| # | Issue | Fix | File |
|---|-------|-----|------|
| 1 | Client-side auth with localStorage | Use httpOnly cookies + middleware | [03-security.md](./03-security.md#critical-client-side-only-authentication) |
| 2 | XSS from unsanitized HTML | Use DOMPurify or JSON format | [03-security.md](./03-security.md#critical-xss-vulnerabilities) |
| 3 | No error boundaries | Add error.tsx to routes | [01-architecture-structure.md](./01-architecture-structure.md#critical-missing-app-router-convention-files) |
| 4 | No loading states | Add loading.tsx to routes | [01-architecture-structure.md](./01-architecture-structure.md#critical-missing-app-router-convention-files) |
| 5 | Everything is Client Component | Convert to Server Components | [01-architecture-structure.md](./01-architecture-structure.md#critical-improper-clientserver-component-separation) |
| 6 | No data caching | Use fetch with cache options | [02-performance-optimization.md](./02-performance-optimization.md#critical-no-data-caching-strategy) |
| 7 | No CSRF protection | Use Server Actions | [03-security.md](./03-security.md#critical-no-csrf-protection) |
| 8 | No input validation | Add Zod validation | [03-security.md](./03-security.md#critical-no-input-validation) |
| 9 | No keyboard navigation | Add keyboard event handlers | [06-accessibility.md](./06-accessibility.md#critical-no-keyboard-navigation-support) |
| 10 | Missing semantic HTML | Use proper HTML5 elements | [06-accessibility.md](./06-accessibility.md#critical-missing-semantic-html) |

---

## ⚡ Quick Fixes

### 1. Convert Page to Server Component

❌ **Before:**
```typescript
'use client'
export default function Page() {
  const [data, setData] = useState(null)
  useEffect(() => { fetchData() }, [])
  return <div>{data}</div>
}
```

✅ **After:**
```typescript
// Server Component (no 'use client')
async function getData() {
  const res = await fetch('...', { next: { revalidate: 60 } })
  return res.json()
}

export default async function Page() {
  const data = await getData()
  return <div>{data}</div>
}
```

---

### 2. Add Error Boundary

Create `error.tsx` in any route:
```typescript
'use client'

export default function Error({ error, reset }: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

---

### 3. Add Loading State

Create `loading.tsx` in any route:
```typescript
export default function Loading() {
  return (
    <div className="flex items-center justify-center">
      <div className="animate-spin h-8 w-8 border-b-2 border-gray-900" />
    </div>
  )
}
```

---

### 4. Secure Authentication

❌ **Before:**
```typescript
localStorage.setItem('access_token', token)
```

✅ **After:**
```typescript
// actions/auth.ts
'use server'
import { cookies } from 'next/headers'

export async function login(email: string, password: string) {
  const response = await fetch('...')
  const { access_token } = await response.json()
  
  const cookieStore = await cookies()
  cookieStore.set('access_token', access_token, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // 7 days
  })
}
```

---

### 5. Add Input Validation

```typescript
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

// Server Action
'use server'
export async function loginAction(formData: FormData) {
  const validated = schema.safeParse({
    email: formData.get('email'),
    password: formData.get('password'),
  })
  
  if (!validated.success) {
    return { errors: validated.error.flatten().fieldErrors }
  }
  
  // Proceed with validated data
}
```

---

### 6. Sanitize HTML

```typescript
import DOMPurify from 'dompurify'

// Before rendering
const clean = DOMPurify.sanitize(userHtml, {
  ALLOWED_TAGS: ['p', 'br', 'strong', 'em'],
})

<div dangerouslySetInnerHTML={{ __html: clean }} />
```

---

### 7. Add Proper Types

❌ **Before:**
```typescript
export default function Page() {
  const params = useParams()
  const id = params.id as string // Manual assertion
}
```

✅ **After:**
```typescript
interface PageProps {
  params: Promise<{ id: string }>
}

export default async function Page({ params }: PageProps) {
  const { id } = await params // Properly typed
}
```

---

### 8. Add Suspense Boundary

```typescript
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <h1>Page Title</h1>
      
      <Suspense fallback={<LoadingSkeleton />}>
        <AsyncComponent />
      </Suspense>
    </div>
  )
}

async function AsyncComponent() {
  const data = await fetchData()
  return <div>{data}</div>
}
```

---

### 9. Add Keyboard Navigation to Modal

```typescript
'use client'

export function Modal({ isOpen, onClose }: Props) {
  useEffect(() => {
    if (!isOpen) return
    
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])
  
  if (!isOpen) return null
  
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {/* Modal content */}
    </div>
  )
}
```

---

### 10. Add Semantic HTML

❌ **Before:**
```typescript
<div className="nav">
  <div>
    <a href="/">Home</a>
    <a href="/about">About</a>
  </div>
</div>
```

✅ **After:**
```typescript
<nav aria-label="Main navigation">
  <ul role="list">
    <li><a href="/">Home</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>
```

---

## 🔍 Common Patterns

### Data Fetching Pattern (Server Component)

```typescript
// With caching
async function getData() {
  const res = await fetch('https://api.example.com/data', {
    next: { 
      revalidate: 3600, // Revalidate every hour
      tags: ['data'] // For on-demand revalidation
    }
  })
  
  if (!res.ok) throw new Error('Failed to fetch')
  return res.json()
}

export default async function Page() {
  const data = await getData()
  return <DataDisplay data={data} />
}
```

### Mutation Pattern (Server Action)

```typescript
// actions/data.ts
'use server'

import { revalidateTag } from 'next/cache'

export async function createItem(formData: FormData) {
  const item = formData.get('item')
  
  await fetch('https://api.example.com/items', {
    method: 'POST',
    body: JSON.stringify({ item }),
  })
  
  revalidateTag('data') // Revalidate cached data
}

// Client component
'use client'

import { createItem } from '@/actions/data'

export function Form() {
  return (
    <form action={createItem}>
      <input name="item" />
      <button type="submit">Create</button>
    </form>
  )
}
```

### Error Handling Pattern

```typescript
// lib/errors.ts
export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500
  ) {
    super(message)
  }
}

// Usage
try {
  await operation()
} catch (error) {
  if (error instanceof AppError) {
    toast.error(error.message)
  } else {
    toast.error('An unexpected error occurred')
  }
  
  logger.error('Operation failed', { error })
}
```

---

## 📦 Essential Packages

### Install These First

```bash
# Security
npm install dompurify zod
npm install --save-dev @types/dompurify

# Testing
npm install --save-dev vitest @testing-library/react
npm install --save-dev @playwright/test

# Development
npm install --save-dev prettier
npm install --save-dev @next/bundle-analyzer
```

### Remove These

```bash
# Replace axios with fetch
npm uninstall axios

# Remove if not using
npm uninstall yjs y-websocket  # If not implementing collaboration yet
```

---

## 🎯 Priority Order

### Day 1 (8 hours)
1. httpOnly cookies (2h)
2. Server-side auth middleware (2h)
3. Input validation with Zod (2h)
4. HTML sanitization (2h)

### Day 2 (8 hours)
5. Add error.tsx files (2h)
6. Add loading.tsx files (2h)
7. Convert 3-4 pages to Server Components (4h)

### Day 3 (8 hours)
8. Implement data caching (3h)
9. Add Suspense boundaries (2h)
10. Configure next/image (1h)
11. Code splitting for editor (2h)

### Week 1 Complete
- Security: 80% complete
- Architecture: 60% complete
- Performance: 40% complete

---

## 🛠️ Useful Commands

```bash
# Type checking
npm run type-check

# Lint
npm run lint

# Build
npm run build

# Analyze bundle
ANALYZE=true npm run build

# Test
npm run test

# E2E tests
npx playwright test
```

---

## 📱 VS Code Snippets

Add to `.vscode/snippets.json`:

```json
{
  "Server Component": {
    "prefix": "nsc",
    "body": [
      "async function getData() {",
      "  const res = await fetch('$1', {",
      "    next: { revalidate: 3600 }",
      "  })",
      "  return res.json()",
      "}",
      "",
      "export default async function ${2:Page}() {",
      "  const data = await getData()",
      "  return <div>{data}</div>",
      "}"
    ]
  },
  "Server Action": {
    "prefix": "nsa",
    "body": [
      "'use server'",
      "",
      "export async function ${1:actionName}(formData: FormData) {",
      "  const data = formData.get('${2:field}')",
      "  ",
      "  // Validation",
      "  ",
      "  // Mutation",
      "  ",
      "  revalidatePath('${3:/path}')",
      "}"
    ]
  }
}
```

---

## 📚 Essential Reading

1. **Start Here:** [Executive Summary](./00-executive-summary.md)
2. **Security First:** [Security Audit](./03-security.md)
3. **Architecture:** [Architecture Audit](./01-architecture-structure.md)
4. **Performance:** [Performance Audit](./02-performance-optimization.md)

---

## 🔗 Quick Links

- [Next.js Docs](https://nextjs.org/docs)
- [App Router](https://nextjs.org/docs/app)
- [Server Actions](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)
- [Caching](https://nextjs.org/docs/app/building-your-application/caching)
- [Security Best Practices](https://nextjs.org/docs/app/building-your-application/security)

---

**Last Updated:** November 25, 2025
