# Frontend Coding Standards

**For AI Agents**: Follow these rules exactly. Do not deviate.

---

## 1. API Calls

### Protected Endpoints (Require Auth)

**USE axios client:**
```typescript
import { documentsAPI, blogAPI, sessionsAPI, authAPI } from '@/lib/api'

await documentsAPI.list()
await blogAPI.generate({ document_ids, session_id })
await sessionsAPI.create({ name })
```

**For streaming, USE authorizedFetch:**
```typescript
import { authorizedFetch, API_URL } from '@/lib/api'

await authorizedFetch(`${API_URL}/api/v1/blog/${id}/refine`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ feedback }),
})
```

**NEVER use raw fetch() for protected endpoints.**

---

## 2. Component Types

### Client Component (interactive)
```typescript
'use client'  // REQUIRED at top of file

import { useState } from 'react'
import { blogAPI } from '@/lib/api'

export default function MyClient() {
  const [data, setData] = useState(null)
  const handleClick = async () => { await blogAPI.delete(id) }
  return <button onClick={handleClick}>Delete</button>
}
```

### Server Component (data fetching)
```typescript
// NO 'use client' directive
import { getDocuments } from '@/lib/api-server'
import MyClient from './my-client'

export default async function Page() {
  const docs = await getDocuments()
  return <MyClient documents={docs} />
}
```

**Rule**: If it uses `onClick`, `useState`, `useEffect` → Client Component.

---

## 3. File Naming

```
page.tsx           → Server Component (Next.js route)
*-client.tsx       → Client Component
@/lib/api.ts       → Client-side API calls
@/lib/api-server.ts → Server-side API calls
```

---

## 4. Constants

```typescript
// ALWAYS use
import { API_URL } from '@/lib/api'

// NEVER hardcode
fetch('http://localhost:8000/...')  // WRONG
fetch('/api/v1/...')                // WRONG
```

**Ports**: Frontend=3002, Backend=8002

---

## 5. Types

```typescript
// REQUIRED - explicit types
const draft: BlogDraft = response.data

// FORBIDDEN
const data: any = response.data
// @ts-ignore
```

---

## 6. Error Handling

```typescript
try {
  await api.delete(id)
} catch (error) {
  alert(error instanceof Error ? error.message : 'Operation failed')
}
```

**Always show errors to user. Never silent catch.**

---

## 7. Auth

- Tokens are in httpOnly cookies (managed by backend)
- `client_token` cookie is readable for axios interceptor
- **NEVER store tokens in localStorage or state**
- Middleware handles token refresh automatically

---

## 8. Before Implementing

1. Check `@/lib/api.ts` for existing API methods
2. Check similar pages for patterns
3. Check `@/types/api.ts` for types

---

## 9. Checklist

- [ ] API calls use axios client or `authorizedFetch`
- [ ] Client components have `'use client'`
- [ ] No hardcoded URLs
- [ ] No `any` types
- [ ] Errors shown to user

---

*Violations of these rules will cause auth failures and runtime errors.*
