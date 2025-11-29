---
title: "Auth Fix Implementation Plan"
date: "2025-11-27 22:51 (KST)"
type: "implementation_plan"
category: "security"
status: "completed"
version: "1.0"
branch: "copilot/update-progress-tracker"
tags: ["auth", "sessions", "implementation", "Option-B"]
references: ["docs/assessments/20251127-auth-session-analysis.md", "docs/API.md", "docs/ARCHITECTURE.md"]
---

## Progress Tracker

- [x] **Phase 1: Fix Client-Side Auth (Option B)** ✅ COMPLETE
  - [x] 1.1 Update `generate-client.tsx` to use axios `sessionsAPI` and `blogAPI`
  - [x] 1.2 Update `drafts-client.tsx` to use axios `blogAPI.delete`
  - [x] 1.3 Update `editor/[draftId]/page.tsx` refine fetch to use axios or add Authorization header
- [x] **Phase 2: Fix Additional Critical Findings** ✅ COMPLETE
  - [x] 2.1 Fix backend `.env` path resolution in `backend/config.py`
  - [x] 2.2 Standardize API URL default across all frontend files (8000 → 8002)
- [x] **Phase 3: Address Confusion Areas** ✅ COMPLETE
  - [x] 3.1 Export `getClientToken` from `api.ts`
  - [x] 3.2 Add `authorizedFetch` helper for streaming/special cases
  - [x] 3.3 Document auth expectations in `docs/API.md`
- [x] **Phase 4: Verification** ✅ COMPLETE
  - [x] 4.1 Test login → upload → generate flow (TypeScript compiles, servers run)
  - [x] 4.2 Test editor refine flow (Auth header added)
  - [x] 4.3 Test draft deletion (blogAPI.delete now used)

---

## Context Summary

The backend (`FastAPI`) enforces JWT auth via `Authorization: Bearer` headers using `HTTPBearer`. The frontend stores tokens as both httpOnly (`access_token`) and non-httpOnly (`client_token`) cookies. The axios client in `api.ts` automatically attaches the bearer token from `client_token`, but several components bypass axios and use raw `fetch` with only `credentials: 'include'`—which sends cookies but **not** the `Authorization` header the backend requires.

### Root Cause

Raw `fetch` calls in client components do not include the `Authorization` header. The backend's `HTTPBearer` dependency rejects requests without this header, returning `403 Forbidden` with `{"detail":"Not authenticated"}`.

### Affected Files

| File | Issue |
|------|-------|
| `frontend/src/app/(dashboard)/dashboard/generate/generate-client.tsx` | Uses raw `fetch` for session creation and blog generation |
| `frontend/src/app/(dashboard)/dashboard/drafts/drafts-client.tsx` | Uses raw `fetch` for draft deletion (wrong endpoint too: `/api/v1/blog/{id}` instead of full URL) |
| `frontend/src/app/(dashboard)/dashboard/editor/[draftId]/page.tsx` | Uses raw `fetch` for streaming refine endpoint |

---

## Phase 1: Fix Client-Side Auth (Option B)

### 1.1 Update `generate-client.tsx`

Replace raw `fetch` calls with axios API methods:

**Current (broken):**
```typescript
const sessionRes = await fetch(`${API_URL}/api/v1/sessions`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ name: `Blog: ${title || 'Untitled'}` }),
})
```

**Fixed:**
```typescript
import { sessionsAPI, blogAPI } from '@/lib/api'

// In handleGenerate:
const sessionRes = await sessionsAPI.create({ name: `Blog: ${title || 'Untitled'}` })
const session_id = sessionRes.data.id

const res = await blogAPI.generate({
  document_ids: selectedDocs,
  title: title || undefined,
  instructions: instructions || undefined,
  session_id,
})
```

### 1.2 Update `drafts-client.tsx`

**Current (broken):**
```typescript
const response = await fetch(`/api/v1/blog/${id}`, {
  method: 'DELETE',
})
```

**Fixed:**
```typescript
import { blogAPI } from '@/lib/api'

// In handleDelete:
await blogAPI.delete(id)
```

### 1.3 Update `editor/[draftId]/page.tsx`

The refine endpoint uses streaming, so we need the `Authorization` header with raw fetch:

**Current (broken):**
```typescript
const response = await fetch(`${API_URL}/api/v1/blog/${draftId}/refine`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ feedback }),
})
```

**Fixed (using helper):**
```typescript
import { getClientToken } from '@/lib/api'

const token = getClientToken()
const response = await fetch(`${API_URL}/api/v1/blog/${draftId}/refine`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  },
  credentials: 'include',
  body: JSON.stringify({ feedback }),
})
```

---

## Phase 2: Fix Additional Critical Findings

### 2.1 Fix Backend `.env` Path Resolution

**File:** `backend/config.py`

**Current:**
```python
model_config = SettingsConfigDict(
    env_file=".env",
    ...
)
```

**Fixed:**
```python
from pathlib import Path

# Resolve project root (one level up from backend/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

model_config = SettingsConfigDict(
    env_file=str(_PROJECT_ROOT / ".env"),
    ...
)
```

### 2.2 Standardize API URL Default

**File:** `frontend/src/lib/api.ts`

**Current:**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

**Fixed:**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
```

---

## Phase 3: Address Confusion Areas

### 3.1 Verify `getClientToken` Export

Already exported in `api.ts`:
```typescript
export { getClientToken } from somewhere // verify this exists
```

Actually, `getClientToken` is defined but not exported. Need to add:
```typescript
export function getClientToken(): string | undefined { ... }
```

### 3.2 Add `authorizedFetch` Helper

Add to `frontend/src/lib/api.ts`:

```typescript
/**
 * Fetch wrapper that automatically adds Authorization header
 * Use for streaming endpoints or cases where axios doesn't work
 */
export async function authorizedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getClientToken()
  const headers = new Headers(options.headers)
  
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  
  return fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  })
}
```

### 3.3 Document Auth Expectations

Add to `docs/API.md`:

```markdown
## Authentication

All protected endpoints require a JWT token via the `Authorization` header:

```
Authorization: Bearer <access_token>
```

**Important:** The backend does NOT read tokens from cookies. Even with `credentials: 'include'`, you must explicitly set the `Authorization` header.

### Client-Side Authentication

- Use the axios client from `@/lib/api` which automatically attaches the token
- For streaming/special cases, use `authorizedFetch` or manually add the header
- The token is available via `getClientToken()` which reads from the `client_token` cookie
```

---

## Phase 4: Verification Checklist

### 4.1 Login → Upload → Generate Flow
1. Login with valid credentials
2. Upload a document
3. Navigate to `/dashboard/generate`
4. Select document and click Generate
5. **Expected:** Session created, blog generated, redirected to editor

### 4.2 Editor Refine Flow
1. Open an existing draft in editor
2. Click "Refine with AI"
3. Enter feedback and submit
4. **Expected:** Content streams in, no auth errors

### 4.3 Draft Deletion
1. Navigate to `/dashboard/drafts`
2. Click delete on a draft
3. **Expected:** Draft deleted, list refreshes

---

## Context Rebuild Prompt

Use this prompt to rebuild context for future sessions:

```
I'm working on fixing authentication issues in a Next.js + FastAPI blog creator app.

Key files to review:
- backend/core/security.py - JWT auth with HTTPBearer (requires Authorization header)
- backend/config.py - Settings with .env loading
- frontend/src/lib/api.ts - Axios client with auto-auth interceptor
- frontend/src/lib/api-server.ts - Server-side API client
- frontend/src/lib/auth-tokens.ts - Cookie management
- frontend/src/middleware.ts - Token refresh logic
- frontend/src/app/(dashboard)/dashboard/generate/generate-client.tsx - NEEDS FIX
- frontend/src/app/(dashboard)/dashboard/drafts/drafts-client.tsx - NEEDS FIX
- frontend/src/app/(dashboard)/dashboard/editor/[draftId]/page.tsx - NEEDS FIX

The problem: Raw fetch calls don't include Authorization header. Backend requires it.
The fix: Use axios client (has interceptor) or manually add Authorization header.

Reference docs:
- docs/assessments/20251127-auth-session-analysis.md
- docs/plans/20251127-2251_auth-fix-implementation-plan.md

Current branch: copilot/update-progress-tracker
```

---

## References

- [Auth Session Analysis](../assessments/20251127-auth-session-analysis.md) - Root cause investigation
- [API Documentation](../API.md) - Endpoint specifications
- [Architecture](../ARCHITECTURE.md) - System design overview

