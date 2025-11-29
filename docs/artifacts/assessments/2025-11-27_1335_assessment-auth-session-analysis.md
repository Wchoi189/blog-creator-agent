---
title: "Stubborn Auth Failure Investigation"
date: "2025-11-27 13:35 (KST)"
type: "assessment"
category: "troubleshooting"
status: "completed"
version: "1.0"
tags: ["auth", "sessions", "e2e-analysis"]
---

**Progress Tracker**
- [x] Capture environment + branch state
- [x] Trace frontend session-creation path
- [x] Inspect backend auth requirements
- [x] Replay request/response sequence from logs
- [x] Identify failure points & confusion areas
- [x] Evaluate remediation options and adjacent risks

## Context Snapshot
- Backend (`FastAPI`) enforces JWT auth via `Authorization: Bearer` headers using `HTTPBearer` in `backend/core/security.py`.
- Frontend (`Next.js 14`) stores tokens as both httpOnly (`access_token`) and duplicate non-httpOnly (`client_token`) cookies via `setAuthCookies`.
- User workflow: login → upload/process docs (succeeds) → `/dashboard/generate` tries to create a session and receives `{"detail":"Not authenticated"}`.
- Current branch `copilot/update-progress-tracker` already contains multiple pending changes; no recent modifications touch `backend/core/security.py`.

## Observed Symptoms
- Make output shows successful auth for other endpoints (`/api/v1/documents/upload`, `GET /api/v1/auth/me`), but `POST /api/v1/sessions` returns HTTP 403 with `detail="Not authenticated"`.
- The failing call originates from the browser client after navigating to `/dashboard/generate`.
- Backend trace never logs entering `session_service.create_session`; rejection happens in dependency resolution (FastAPI fails to satisfy `Depends(get_current_user_id)` before hitting business logic).

## End-to-End Flow Breakdown
1. **Login (server action):** `frontend/src/actions/auth.ts` posts credentials, receives `{access_token, refresh_token}`, and stores them via `setAuthCookies`. Result: browser now holds `access_token` (httpOnly) and `client_token` (accessible) cookies.
2. **Document uploads/listing:** UI components that rely on `documentsAPI` (axios instance) succeed because `frontend/src/lib/api.ts` attaches `Authorization: Bearer <client_token>` in a request interceptor.
3. **Session creation on Generate page:** `frontend/src/app/(dashboard)/dashboard/generate/generate-client.tsx` bypasses the shared axios client and calls `fetch` directly. Request metadata:
   - Headers: only `Content-Type: application/json`
   - `credentials: 'include'` sends cookies, but there is **no** `Authorization` header.
4. **Backend dependency:** `backend/api/v1/sessions.py` wraps `create_session` with `Depends(get_current_user_id)`. `HTTPBearer` enforces that the token arrives strictly via `Authorization` header; cookies are ignored.
5. **Result:** FastAPI raises `HTTPException(status_code=403, detail="Not authenticated")`, which propagates to the frontend error handler (`Failed to create session: {"detail":"Not authenticated"}`).

## Failure Points & Confusion Areas
- **Dual Auth Patterns:** Parts of the app rely on axios (`docs upload`, `blog editing`), while others use raw `fetch`. The axios client adds `Authorization` automatically; the raw `fetch` path does not. This split obscures the need for a header, explaining why only some pages break.
- **Cookie Misassumption:** UI code assumes httpOnly cookies plus `credentials: 'include'` are enough. That would only work if the backend also inspected cookies, which it currently does not.
- **Inconsistent API URL defaults:** `frontend/src/lib/api.ts` falls back to `http://localhost:8000` whereas other modules default to `http://localhost:8002`. If env vars go missing, different parts of the app would silently target different ports. Not the immediate blocker, but a latent footgun.
- **Lack of shared helper:** There is no exported helper for “authorized fetch” on the client. Every component implements its own strategy, increasing drift risk.

## Options & Evaluation
| Option | Description | Pros | Cons / Risks |
| --- | --- | --- | --- |
| A | Update all client-side fetches (starting with `generate-client.tsx`) to read `client_token` and set `Authorization: Bearer <token>` | Minimal backend change, aligns with existing axios pattern, quick relief | Requires DOM access; must guard for SSR. Need to ensure `client_token` is always present and up to date |
| B | Replace ad-hoc fetches with shared axios client (`sessionsAPI.create`) | Removes duplicate networking logic, auto-inherits interceptors, consistent error handling | Some components are Server Components where axios (browser-only) is unavailable; need wrappers to call server actions |
| C | Enhance backend `get_current_user_id` to accept tokens from cookies (e.g., read `access_token` if header missing) | Simplifies frontend (no need for Authorization header) | Weakens separation of concerns, mixes cookies with bearer auth, increases CSRF exposure unless additional defenses added |
| D | Move session creation into a server action so it can read httpOnly `access_token` via `cookies()` and call backend with proper headers server-side | Keeps sensitive logic off the client, consistent with Next best practices | Requires re-architecting the generate flow, more effort than Options A/B |

**Recommendation:** Implement Option B for immediate consistency (call `sessionsAPI.create` and `blogAPI.generate` inside `handleGenerate`). Supplement with Option A guard to ensure any future raw fetches include `Authorization`. Option D can be a follow-up refactor if we want stricter security boundaries.

## Additional Critical Findings
- **Environment file discovery:** Earlier Redis outage stemmed from `.env` file not being discoverable from the backend working directory. Although fixed manually, this should be codified (e.g., adjust `SettingsConfigDict(env_file="../.env")`) to prevent future silent misconfigurations.
- **API base URL drift:** The axios client defaulting to `http://localhost:8000` while other modules point to `8002` can lead to hard-to-debug mismatches if `NEXT_PUBLIC_API_URL` is absent in certain environments (e.g., Storybook, unit tests). Consider centralizing API URL resolution.

## Next Steps
1. Patch `generate-client.tsx` (and any other raw fetch callers) to use the shared axios client or manually attach `Authorization`.
2. Add tests or runtime guards that assert an `Authorization` header is present before hitting protected endpoints.
3. Document the expectation (“Backend only honors bearer headers”) in `docs/API.md` and consider linting or helper utilities to enforce compliance.
4. Evaluate a server-action-based session creation path for longer-term resilience and to reduce exposure of access tokens to client-side JavaScript.

