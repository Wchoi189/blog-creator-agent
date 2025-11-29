---
title: "Authentication Session Fix Plan"
date: "2025-11-27 22:51 (KST)"
type: "implementation_plan"
category: "security"
status: "active"
version: "1.0"
branch: "copilot/update-progress-tracker"
priority: "critical"
estimated_hours: "4-6"
tags: ["authentication", "session-management", "frontend-backend-integration", "critical-bug", "api-consistency"]
references: ["docs/assessments/20251127-auth-session-analysis.md", "docs/API.md", "docs/ARCHITECTURE.md"]
---

# Authentication Session Fix Plan

## Progress Tracker

- [ ] **Phase 1: Core Auth Infrastructure**
  - [ ] Fix backend .env loading (config.py path issue)
  - [ ] Implement Option B: Axios client standardization
  - [ ] Create auth token utilities consolidation

- [ ] **Phase 2: Frontend API Consistency**
  - [ ] Update generate-client.tsx to use axios client
  - [ ] Audit all raw fetch() calls for auth headers
  - [ ] Implement client-side token validation

- [ ] **Phase 3: Backend Security Validation**
  - [ ] Add comprehensive auth middleware testing
  - [ ] Implement proper error handling for auth failures
  - [ ] Add session state validation

- [ ] **Phase 4: Testing & Validation**
  - [ ] Create auth integration tests
  - [ ] Test session lifecycle (login → generate → logout)
  - [ ] Validate cookie-based auth flow

## Problem Summary

**Root Cause:** Frontend raw `fetch()` calls bypass authentication by not including Bearer tokens in Authorization headers, causing 401/403 responses from FastAPI endpoints requiring `get_current_user_id()` dependency.

**Impact:** Users cannot create blog generation sessions despite being logged in, breaking core functionality.

**Discovered Issues:**
1. **Primary:** `generate-client.tsx` uses raw `fetch()` without auth headers
2. **Secondary:** Backend config loads wrong `.env` file (relative path issue)
3. **Tertiary:** Inconsistent API URL configuration across frontend files
4. **Additional:** Mixed authentication patterns (Server Actions vs Client Components)

## Recommended Implementation: Option B - Axios Client Standardization

### Why Option B?
- **Minimal Risk:** Reuses existing, working axios infrastructure
- **Fast Implementation:** ~2-3 hours vs 6+ for full server action migration
- **Proven Pattern:** Already used successfully in upload/document flows
- **Backward Compatible:** Doesn't break existing Server Actions

## Phase 1: Core Auth Infrastructure Fixes

### 1.1 Fix Backend Environment Loading
**Issue:** `backend/config.py` loads `.env` from wrong directory

**Current Code:**
```python:backend/config.py
model_config = SettingsConfigDict(
    env_file=".env",  # Relative to backend/ directory
    ...
)
```

**Fix:**
```python:backend/config.py
model_config = SettingsConfigDict(
    env_file="../.env",  # Load from project root
    ...
)
```

**Validation:**
- [ ] Verify Redis connection works with `redis://redis:6379/0`
- [ ] Test backend starts without connection errors
- [ ] Confirm environment variables load correctly

### 1.2 Consolidate Frontend API Configuration
**Issue:** Multiple API URL definitions with potential mismatches

**Current Issues:**
- `frontend/src/lib/api.ts`: `http://localhost:8000`
- `frontend/src/actions/auth.ts`: `http://localhost:8002`
- `frontend/src/middleware.ts`: `http://localhost:8002`

**Fix:** Create centralized API config

**New File:** `frontend/src/lib/api-config.ts`
```typescript
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002',
  TIMEOUT: 30000,
} as const
```

**Update all files to import from this central config**

### 1.3 Enhance Auth Token Utilities
**Issue:** Token management scattered across multiple files

**Consolidate into:** `frontend/src/lib/auth-client.ts`

```typescript
import { API_CONFIG } from './api-config'

export function getClientToken(): string | undefined {
  // Consolidated token extraction logic
}

export function createAuthenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getClientToken()
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      ...(token && { 'Authorization': `Bearer ${token}` })
    },
    credentials: 'include'
  })
}
```

## Phase 2: Frontend API Consistency Implementation

### 2.1 Update Generate Client Component
**Target:** `frontend/src/app/(dashboard)/dashboard/generate/generate-client.tsx`

**Current Problem Code:**
```typescript
const sessionRes = await fetch(`${API_URL}/api/v1/sessions`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // Missing Authorization header
  body: JSON.stringify({ name: `Blog: ${title || 'Untitled'}` }),
})
```

**Fix:**
```typescript
import { sessionsAPI } from '@/lib/api'

// Replace raw fetch with axios
const sessionRes = await sessionsAPI.create({
  name: `Blog: ${title || 'Untitled'}`
})
```

**Alternative (if keeping fetch):**
```typescript
import { createAuthenticatedFetch, API_CONFIG } from '@/lib/auth-client'

const sessionRes = await createAuthenticatedFetch(
  `${API_CONFIG.BASE_URL}/api/v1/sessions`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: `Blog: ${title || 'Untitled'}` }),
  }
)
```

### 2.2 Audit All Raw Fetch Calls
**Search for patterns to fix:**
- [ ] `fetch.*credentials.*include` without Authorization header
- [ ] Direct API calls in client components
- [ ] Inconsistent API URL usage

**Files to check:**
- [ ] All `.tsx` files in dashboard components
- [ ] Client-side utilities
- [ ] Any remaining raw fetch usage

### 2.3 Add Client-Side Auth Validation
**New utility:** `frontend/src/lib/auth-validation.ts`

```typescript
export function validateAuthState(): { isValid: boolean; error?: string } {
  // Check token existence and validity
  // Return validation result
}

export function handleAuthError(error: Response): void {
  if (error.status === 401) {
    // Redirect to login
    window.location.href = '/login'
  }
}
```

## Phase 3: Backend Security Validation

### 3.1 Enhance Error Handling
**Update:** `backend/core/security.py`

**Add better error messages:**
```python
async def get_current_user_id(...) -> str:
    try:
        payload = decode_token(token)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token decode failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Add more specific validation messages
    if not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
        )
```

### 3.2 Add Session State Validation
**Update:** `backend/services/session_service.py`

**Add user validation:**
```python
async def create_session(self, user_id: str, session_data: SessionCreate) -> Session:
    # Validate user exists and is active
    user_exists = await self.redis.exists(f"user:{user_id}")
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user session"
        )

    # Continue with session creation...
```

## Phase 4: Testing & Validation

### 4.1 Create Integration Tests
**New file:** `tests/integration/test_auth_flow.py`

```python
async def test_full_auth_flow():
    """Test: login → create session → generate blog → logout"""
    # 1. Register/Login user
    # 2. Create session (this was failing)
    # 3. Generate blog draft
    # 4. Verify session state
    # 5. Logout and verify cleanup
```

### 4.2 Frontend Auth Flow Tests
**New file:** `frontend/__tests__/auth-flow.test.ts`

```typescript
describe('Authentication Flow', () => {
  test('should create session with valid auth', async () => {
    // Mock authenticated state
    // Test session creation
    // Verify API calls include auth headers
  })
})
```

### 4.3 Manual Testing Checklist
- [ ] Login flow works
- [ ] Session creation succeeds
- [ ] Blog generation completes
- [ ] Logout cleans up state
- [ ] Invalid tokens redirect properly
- [ ] Expired tokens refresh automatically

## Additional Critical Findings & Resolutions

### Finding A: API URL Inconsistencies
**Resolution:** ✅ **Implemented** - Centralized config in `api-config.ts`

### Finding B: Backend .env Path Issue
**Resolution:** ✅ **To Implement** - Update `backend/config.py` env_file path

### Finding C: Mixed Auth Patterns
**Resolution:** **Short-term** - Standardize on axios client. **Long-term** - Consider full Server Actions migration when time allows.

### Finding D: Missing Auth Headers
**Resolution:** ✅ **To Implement** - Update `generate-client.tsx` and audit all fetch calls

### Finding E: Poor Error Messages
**Resolution:** ✅ **To Implement** - Enhance backend error responses

## Risk Assessment

### Low Risk Changes:
- Backend config path fix
- API URL centralization
- Auth token utilities consolidation

### Medium Risk Changes:
- Component API call refactoring
- Error handling improvements

### High Risk Changes:
- None identified (all changes are additive/fixes)

## Rollback Plan

If issues arise:
1. **Config issues:** Revert `backend/config.py` to original path
2. **Frontend issues:** Components fall back to existing Server Actions
3. **API issues:** Raw fetch calls still work for non-auth endpoints

## Success Criteria

- [ ] Users can successfully create blog generation sessions
- [ ] No 401/403 errors during authenticated operations
- [ ] Consistent API URL usage across frontend
- [ ] Clear error messages for auth failures
- [ ] All integration tests pass

---

## Reusable Context Rebuild Prompt

```
I'm working on fixing persistent authentication issues in our blog-creator-agent project. The main problem is that raw fetch() calls in client components don't include Authorization headers, causing 401 errors on protected endpoints.

Key files to examine:
- frontend/src/app/(dashboard)/dashboard/generate/generate-client.tsx (raw fetch issue)
- backend/core/security.py (auth dependency)
- frontend/src/lib/api.ts (working axios client)
- backend/config.py (env loading issue)
- docs/assessments/20251127-auth-session-analysis.md (full analysis)

Current status: Planning phase complete. Need to implement Option B (axios standardization) with fixes for:
1. Backend .env path loading
2. Frontend API URL consolidation
3. Generate component auth headers
4. Enhanced error handling

Please help implement the remaining fixes from the plan.
```

## Reference Documents

- **Analysis Document:** `docs/assessments/20251127-auth-session-analysis.md`
- **API Documentation:** `docs/API.md`
- **Architecture Overview:** `docs/ARCHITECTURE.md`
- **Authentication Implementation:** `backend/core/security.py`
- **Frontend Auth Actions:** `frontend/src/actions/auth.ts`
- **Current Branch:** `copilot/update-progress-tracker`

---

*Document generated: 2025-11-27T22:51:00Z*
*Next action: Begin Phase 1 implementation*
