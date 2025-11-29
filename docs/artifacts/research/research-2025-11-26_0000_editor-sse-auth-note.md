---
title: "Editor Page SSE Authentication Issue"
date: "2025-11-26 00:00 (KST)"
type: "research"
category: "security"
status: "active"
version: "1.0"
tags: ["sse", "auth", "editor", "security"]
---

# Editor Page SSE Authentication Issue

**File**: `frontend/src/app/(dashboard)/dashboard/editor/[draftId]/page.tsx`
**Issue**: Line 67 uses `localStorage.getItem('access_token')` for SSE
**Status**: Known limitation - deferred

---

## Problem

The editor page uses Server-Sent Events (SSE) via `EventSource` for real-time content streaming during blog refinement:

```typescript
const token = localStorage.getItem('access_token');
const eventSource = new EventSource(
  `${API_URL}/api/v1/blog/${draftId}/refine?feedback=${encodeURIComponent(feedback)}&token=${token}`
);
```

**Why this is problematic**:
1. Uses localStorage for auth token (XSS vulnerability)
2. EventSource API doesn't support custom headers
3. httpOnly cookies can't be accessed from JavaScript

---

## Solutions (Ordered by preference)

### Option 1: Server-Side Streaming (Recommended)
**Approach**: Convert editor to use Server Actions with streaming response

```typescript
// Server Action with streaming
'use server'
export async function refineBlogStream(draftId: string, feedback: string) {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      // Server-side fetch with httpOnly cookies
      const response = await fetch(`${API_URL}/api/v1/blog/${draftId}/refine`, {
        method: 'POST',
        headers: await getAuthHeaders(),
        body: JSON.stringify({ feedback }),
      })
      
      const reader = response.body.getReader()
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        controller.enqueue(value)
      }
      controller.close()
    }
  })
  
  return stream
}
```

**Benefits**:
- No client-side token access needed
- Works with httpOnly cookies
- More secure

**Drawbacks**:
- Requires refactoring editor component
- More complex implementation

### Option 2: Backend Cookie Support for SSE
**Approach**: Modify backend to accept cookies for SSE endpoints

```python
# Backend: Accept cookies for SSE
@app.get("/api/v1/blog/{draft_id}/refine")
async def refine_blog_sse(
    draft_id: str,
    feedback: str,
    request: Request,  # Access cookies from request
):
    # Get token from cookie instead of query param
    token = request.cookies.get("access_token")
    # ... rest of SSE logic
```

**Benefits**:
- Minimal frontend changes
- Works with httpOnly cookies
- Cleaner URL (no token in query string)

**Drawbacks**:
- Requires backend changes
- Need to verify EventSource sends cookies (it should with credentials)

### Option 3: Temporary Token Endpoint
**Approach**: Create endpoint that issues short-lived tokens for SSE

```typescript
// Server Action to get temporary token
'use server'
export async function getTemporaryToken() {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')
  
  // Call backend to exchange httpOnly cookie for temporary token
  const response = await fetch(`${API_URL}/api/v1/auth/temp-token`, {
    headers: { Authorization: `Bearer ${token.value}` }
  })
  
  const { tempToken } = await response.json()
  return tempToken // Valid for 5 minutes only
}

// Client: Use temporary token
const tempToken = await getTemporaryToken()
const eventSource = new EventSource(
  `${API_URL}/api/v1/blog/${draftId}/refine?feedback=${feedback}&token=${tempToken}`
)
```

**Benefits**:
- Works with current architecture
- No localStorage usage
- Short-lived tokens limit security risk

**Drawbacks**:
- Still exposes tokens to JavaScript (albeit short-lived)
- Requires backend endpoint

### Option 4: Disable Editor Refine Feature
**Approach**: Remove the SSE refine feature temporarily

**Benefits**:
- Immediate security fix
- Simple to implement

**Drawbacks**:
- Loss of functionality
- Not a real solution

---

## Current Status

**Temporary Workaround**: The editor page still uses localStorage for SSE authentication. This is the ONLY remaining localStorage usage for auth in the entire application.

**Risk Assessment**:
- **Exposure**: Only affects editor page refine feature
- **Scope**: Single line of code
- **Mitigation**: All other pages use httpOnly cookies
- **Priority**: MEDIUM (should fix but not blocking)

---

## Recommendation

**For immediate security improvement**: 
- Keep current implementation but document the risk
- Add TODO comment in code
- Plan to implement Option 2 (Backend Cookie Support) in next sprint

**For complete security**:
- Implement Option 1 (Server-Side Streaming) - best long-term solution
- Requires coordination with backend team

---

## Implementation Checklist (When fixing)

- [ ] Choose solution approach
- [ ] Update backend if needed (Option 2 or 3)
- [ ] Refactor editor component
- [ ] Test SSE streaming with new auth method
- [ ] Verify no localStorage usage
- [ ] Update documentation
- [ ] Security verification

---

**Created**: 2025-11-26  
**Status**: Documented - Implementation deferred  
**Priority**: MEDIUM  
**Security Risk**: LOW (isolated to one feature)
