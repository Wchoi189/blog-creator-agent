# AUTONOMOUS WORKER INSTRUCTIONS v2 - HYBRID APPROACH
# Audit Resolution + Next.js 15 Upgrade Combined

**Project:** Blog Creator Agent - Next.js Frontend  
**Objective:** Complete audit resolutions while upgrading to Next.js 15  
**Approach:** HYBRID - Fix issues using Next.js 15 patterns from the start  
**Mode:** AUTONOMOUS with progress tracking  

---

## CRITICAL UPDATES FROM v1

### What Changed?
1. **Decision**: Perform Next.js 15 upgrade **during** audit fixes (not after)
2. **Rationale**: Audit fixes align with Next.js 15 requirements
3. **Status**: Previous session completed ~40% of work with mixed patterns
4. **Critical Issue**: Mixed authentication (httpOnly cookies + localStorage)

### Why Hybrid Approach?
- Avoid rework: Fix issues with Next.js 15 patterns from start
- Save time: Many audit fixes are required for Next.js 15 anyway
- Better DX: Use latest features while fixing issues
- Future-proof: No need for another upgrade soon

---

## CRITICAL RULES

1. **ALWAYS update PROGRESS-TRACKER.md** after each major task
2. **COMMIT frequently** - after each completed item
3. **FIX CRITICAL ISSUES FIRST** - especially authentication
4. **USE Next.js 15 patterns** from the start
5. **TEST after each phase** - don't accumulate issues
6. **DOCUMENT changes** - update implementation notes
7. **REMOVE mixed patterns** - consolidate to one approach
8. **VERIFY builds** - ensure no TypeScript errors

---

## EXECUTION WORKFLOW

```
CRITICAL FIXES → UPGRADE → ARCHITECTURE → OPTIMIZATION → POLISH → COMPLETE
     ↓              ↓           ↓              ↓           ↓         ↓
   Security     Next.js 15   Server Comp.  Performance  Access.   Tests
   (1-2 days)   (1-2 days)   (2 days)      (1 day)      (1 day)  (1 day)
```

---

## PHASE 0: CRITICAL FIXES (IMMEDIATE - 4-6 hours)

### Priority 1: Fix Authentication Security Issue

**Problem**: Mixed authentication pattern
- Server Actions use httpOnly cookies ✅
- But `lib/api.ts` uses localStorage ❌
- Creates XSS vulnerability

**Solution**:

1. **Create Server-Side API Client** (`lib/api-server.ts`):
```typescript
import { cookies } from 'next/headers'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

async function getAuthHeaders() {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')
  
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token.value}` }),
  }
}

export async function apiGet<T>(endpoint: string): Promise<T> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers,
    next: { revalidate: 60 },
  })
  
  if (!res.ok) throw new Error(`API Error: ${res.statusText}`)
  return res.json()
}

export async function apiPost<T>(endpoint: string, data: any): Promise<T> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
    cache: 'no-store',
  })
  
  if (!res.ok) throw new Error(`API Error: ${res.statusText}`)
  return res.json()
}

// Add apiPut, apiDelete similarly
```

2. **Update Client Components**:
   - Remove `authStore` usage (if uses localStorage)
   - Use Server Components for data fetching
   - Use Server Actions for mutations
   - Keep client components minimal (interactivity only)

3. **Remove localStorage References**:
```bash
# Search for localStorage usage
grep -r "localStorage" frontend/src/

# Each must be replaced with:
# - Server Actions for mutations
# - Server Components for data fetching
# - Cookies for authentication (already done in auth.ts)
```

**Verification**:
```bash
# Should find NO localStorage references for auth
grep -r "localStorage.getItem('access_token')" frontend/src/
# Should return empty

# Build should succeed
cd frontend && npm run build
```

---

## PHASE 1: NEXT.JS 15 UPGRADE (1-2 days)

### Task 1.1: Update Core Dependencies

```bash
cd frontend

# Backup package.json
cp package.json package.json.backup

# Update to Next.js 15 + React 19
npm install next@latest react@latest react-dom@latest

# Update TypeScript types
npm install -D @types/react@latest @types/react-dom@latest

# Update TipTap to v3 (major change)
npm install @tiptap/react@latest @tiptap/starter-kit@latest @tiptap/extension-link@latest @tiptap/extension-placeholder@latest

# Update ESLint
npm install -D eslint@latest eslint-config-next@latest
```

### Task 1.2: Update TypeScript Config

No changes needed - already compatible.

### Task 1.3: Fix Async Request APIs

**Before (Next.js 14)**:
```typescript
// app/editor/[draftId]/page.tsx
export default function EditorPage({ params }: { params: { draftId: string } }) {
  const { draftId } = params
  return <Editor draftId={draftId} />
}
```

**After (Next.js 15)**:
```typescript
// types/next.ts
export interface PageProps<T = Record<string, string>> {
  params: Promise<T>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}

// app/editor/[draftId]/page.tsx
import type { PageProps } from '@/types/next'

export default async function EditorPage({ 
  params 
}: PageProps<{ draftId: string }>) {
  const { draftId } = await params
  return <EditorClient draftId={draftId} />
}

// Create separate client component
'use client'
function EditorClient({ draftId }: { draftId: string }) {
  return <Editor draftId={draftId} />
}
```

**Files to Update**:
- `app/(dashboard)/dashboard/editor/[draftId]/page.tsx`
- Any other page using `params` or `searchParams`

### Task 1.4: Update Fetch Caching

**Next.js 15 Requirement**: Explicit caching

```typescript
// Before (implicit cache)
const res = await fetch('/api/data')

// After (explicit cache)
const res = await fetch('/api/data', {
  next: { revalidate: 3600 },  // Cache for 1 hour
})

// OR no cache
const res = await fetch('/api/data', {
  cache: 'no-store'
})
```

Update all fetch calls in:
- `lib/api-server.ts` (use in apiGet/apiPost)
- Server Components
- Server Actions

### Task 1.5: Update TipTap Editor

**TipTap v2 → v3 Changes**:

```typescript
// Before (v2)
import StarterKit from '@tiptap/starter-kit'

// After (v3)
import { StarterKit } from '@tiptap/starter-kit'

// Add new config
const editor = useEditor({
  extensions: [StarterKit],
  content: content,
  immediatelyRender: false,  // Important for SSR!
})
```

### Task 1.6: Test Upgrade

```bash
# Build should succeed
npm run build

# Check for errors
npm run lint

# Test dev server
npm run dev
```

**Commit**: `"Phase 1: Upgrade to Next.js 15 + React 19 + TipTap v3"`

---

## PHASE 2: ARCHITECTURE (USING NEXT.JS 15 PATTERNS)

### Task 2.1: Convert Pages to Server Components

**Pattern**:
```typescript
// Server Component (default)
async function getData() {
  const data = await apiGet('/endpoint')
  return data
}

export default async function Page() {
  const data = await getData()
  return <ClientComponent data={data} />
}

// Separate client component
'use client'
function ClientComponent({ data }) {
  // Interactive logic here
  return <div>{/* UI */}</div>
}
```

**Pages to Convert**:
- Dashboard overview
- Documents list
- Drafts list
- Upload page (keep client for interactivity)
- Generate page

### Task 2.2: Update Error Boundaries

Ensure all error.tsx files use proper pattern:
```typescript
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### Task 2.3: Add Metadata API

```typescript
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Page Title | Blog Creator',
  description: 'Page description',
}

export default async function Page() {
  // ...
}
```

**Commit**: `"Phase 2: Architecture - Server Components + metadata"`

---

## PHASE 3: PERFORMANCE OPTIMIZATION

### Task 3.1: Dynamic Import TipTap

```typescript
// components/editor/index.tsx
import dynamic from 'next/dynamic'

const TiptapEditor = dynamic(
  () => import('./TiptapEditor'),
  {
    loading: () => <LoadingSpinner />,
    ssr: false,  // TipTap v3 supports SSR but disable for safety
  }
)

export default TiptapEditor
```

### Task 3.2: Configure next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    formats: ['image/avif', 'image/webp'],
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  experimental: {
    optimizePackageImports: ['lucide-react', 'zustand'],
  },
}

module.exports = nextConfig
```

### Task 3.3: Add Suspense Boundaries

```typescript
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <h1>Title</h1>
      <Suspense fallback={<LoadingSkeleton />}>
        <AsyncComponent />
      </Suspense>
    </div>
  )
}
```

**Commit**: `"Phase 3: Performance - dynamic imports, suspense, config"`

---

## PHASE 4: CODE QUALITY

### Task 4.1: Add Proper Types

Create `types/next.ts`, `types/api.ts`, etc.

### Task 4.2: Create Constants

```typescript
// lib/constants.ts
export const API_TIMEOUTS = {
  DEFAULT: 30000,
  UPLOAD: 300000,
} as const

export const CACHE_DURATIONS = {
  STATIC_DATA: 3600,
  USER_DATA: 60,
} as const
```

### Task 4.3: Create Reusable Components

```typescript
// components/ui/button.tsx
// components/ui/loading-spinner.tsx
// components/ui/card.tsx
```

**Commit**: `"Phase 4: Code quality - types, constants, components"`

---

## PHASE 5: ACCESSIBILITY

### Task 5.1: Update Layout with Semantic HTML

```typescript
<header role="banner">
  <nav aria-label="Main navigation">
    <ul role="list">
      <li><Link href="/">Home</Link></li>
    </ul>
  </nav>
</header>

<main id="main-content" aria-label="Main content">
  {children}
</main>
```

### Task 5.2: Add Skip Link

```typescript
// app/layout.tsx
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 ..."
>
  Skip to main content
</a>
```

### Task 5.3: Add ARIA Labels

All interactive elements, forms, buttons, links.

**Commit**: `"Phase 5: Accessibility - semantic HTML, ARIA, skip link"`

---

## PHASE 6: CLEANUP

### Task 6.1: Remove Dependencies

```bash
npm uninstall axios  # Replaced with fetch
npm uninstall yjs y-websocket  # If not using
npm update  # Update all packages
```

### Task 6.2: Final Build

```bash
npm run build
npm run lint
```

### Task 6.3: Create Documentation

Create `frontend/IMPLEMENTATION_NOTES.md` with:
- Changes made
- New patterns used
- Dependencies added/removed
- Breaking changes
- Next steps

**Commit**: `"Phase 6: Cleanup - remove axios, update deps, documentation"`

---

## PHASE 7: TESTING (if time allows)

### Task 7.1: Setup Vitest

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

### Task 7.2: Add Test Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui"
  }
}
```

**Commit**: `"Phase 7: Testing setup"`

---

## VALIDATION CHECKLIST

Before completing:

- [ ] No localStorage usage for authentication
- [ ] All pages use async params (Next.js 15)
- [ ] All fetch calls have explicit cache config
- [ ] TipTap v3 working properly
- [ ] Build completes without errors
- [ ] Linting passes
- [ ] No TypeScript errors
- [ ] Error boundaries throughout
- [ ] Loading states throughout
- [ ] Proper semantic HTML
- [ ] ARIA labels added
- [ ] Documentation updated
- [ ] PROGRESS-TRACKER.md updated
- [ ] axios removed
- [ ] Dependencies cleaned up

---

## COMPLETION SUMMARY

After all phases complete, update PROGRESS-TRACKER.md with:
- Total time spent
- All completed items
- Build status
- Test results
- Known issues (if any)
- Recommendations

---

## DIFFERENCES FROM v1

| Aspect | v1 (Original) | v2 (Hybrid) |
|--------|---------------|-------------|
| Approach | Fix then upgrade | Fix while upgrading |
| Next.js Version | Stay on 14 | Upgrade to 15 immediately |
| Fetch Caching | Implicit | Explicit (required in 15) |
| Params | Sync | Async (required in 15) |
| TipTap | v2 | v3 (required for React 19) |
| Timeline | 8 weeks | 6 weeks (less rework) |
| Risk | Low (gradual) | Medium (more changes upfront) |
| Benefits | Safer | Faster, better long-term |

---

**Version**: 2.0  
**Date**: 2025-11-26  
**Status**: Active  
**Previous Version**: See `AUTONOMOUS-WORKER-INSTRUCTIONS.md` (archived approach)

---

**Note**: This replaces v1 instructions. Use this for all future work.
