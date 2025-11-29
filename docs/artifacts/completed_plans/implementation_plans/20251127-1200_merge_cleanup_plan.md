---
title: "Chainlit/Chroma Removal & Auth Merge Plan"
date: "2025-11-27 12:00 (KST)"
type: "implementation_plan"
category: "development"
status: "active"
version: "1.0"
branch: "copilot/update-progress-tracker"
owner: "platform-team"
tags: ["merge", "cleanup", "auth", "dependencies"]
---

**Progress Tracker**  
- Last Completed: Updated docs (README, HANDOVER, SECURITY) to remove ChromaDB/Chainlit references; removed legacy `public/custom.js` and `public/custom.css` Chainlit files; installed Nori Korean tokenizer in Elasticsearch.  
- In Progress: Run tests, then merge PR #4.  
- Next: Next.js 15 upgrade.

## Goals
- ✅ Keep legacy Chainlit UI & ChromaDB fully removed (match `main` commit `c3cda8a`).
- ✅ Preserve performance wins from feature branch while adopting fixed auth/session behavior from `main`.
- ✅ Update `pyproject.toml` / lockfile to drop unused deps.
- ✅ Resolve remaining dashboard 403/401 errors and runtime exceptions.

## High-Level Workstream Checklist
- [x] **Branch Realignment**  
  - [x] Abort current rebase (`git rebase --abort`) to restore the clean feature branch state.  
  - [x] Cherry-pick targeted commits from `main` (auth/session TTL, generate page styling, dependency removals) instead of rebasing wholesale.  
    - Completed target list (from `git cherry` vs `origin/main`):  
      1. `c3cda8a` – Applied with `git cherry-pick -X ours c3cda8a`; imported auth TTL bump, dashboard styling, dependency cleanup, doc/archive moves while preserving backend service implementations.  
  - [x] Ensure `docs/archive/` structure and other new files survive each cherry-pick (snapshot with `git status` before/after).
- [x] **Merge Conflict Resolution**  
  - [x] `backend/core/database.py`: retain Redis/SQL-only path, remove `chromadb` imports, keep any new helper utilities.  
  - [x] `backend/services/blog_service.py` & `document_service.py`: keep OpenAI streaming logic, delete `VectorStoreFactory` remnants, confirm Redis usage aligns with `main`.  
  - [x] Frontend dashboard pages (`frontend/src/app/(dashboard)/...`): reconcile server-component auth guard changes with layout tweaks from `main`.  
  - [x] Auth utilities (`frontend/src/actions/auth.ts`, `frontend/src/lib/api.ts`, `navbar`): ensure 24h session TTL logic surfaces and `api-server.ts` stays the single fetch wrapper.  
  - [x] Docs (`deprecated_chainlit.md`, `deprecated_project_plan.md`): keep only archived copies under `docs/archive/deprecated/` to avoid resurrecting deletions.
- [x] **Authentication Fixes**  
  - [x] Re-enable refresh-token flow (backend `/api/v1/auth/refresh` + middleware-managed cookie rotation) to stop dashboard 401 loops without violating Next.js cookie rules.  
  - [x] Confirm `SESSION_EXPIRE_SECONDS` (24h in `backend/config.py`).  
  - [x] Verify `/api/v1/sessions` POST accepts dashboard origin.  
  - [x] Update `GeneratePage` to use axios client with auth interceptor.  
  - [x] Ensure `/dashboard/settings` uses axios client with Authorization header.
- [x] **Dependency & Config Cleanup**  
  - [x] `pyproject.toml` already clean (no Chainlit/Chroma deps).  
  - [x] Update docs (`README.md`, `HANDOVER.md`, `SECURITY.md`) to state Redis + Elasticsearch only.  
  - [x] Delete remaining Chainlit files (`public/custom.js`, `public/custom.css`).
- [ ] **Testing & Verification**  
  - [ ] Run backend unit tests: `make test-backend` (or `pytest backend/tests`).  
  - [ ] Run frontend lint/test: `pnpm lint && pnpm test`.  
  - [x] Manual QA:  
    - [x] Login/logout cycle verifies httpOnly cookies persist for 24h.  
    - [x] `/dashboard/generate` blog creation works without 403; streaming output renders.  
    - [x] `/dashboard/settings` no longer throws runtime errors; API key list accessible (200).  
    - [x] Document upload + blog regeneration still works with Redis backend.

## Detailed Action Plan
1. **Prep & Safety Nets**  
  - Snapshot current work: `git status`, `git stash push -m "pre-sync"` if necessary.  
  - Abort the interactive rebase that is currently paused on `349e273` (blog generation fixes).  
  - Pull latest `origin/main` and list candidate commits to cherry-pick (auth/session TTL, generate styling, dependency cleanup).  
  - Document the chosen cherry-picks in `PROGRESS-TRACKER.md` for future reference.
2. **Backend Conflict Walkthrough**  
  - Lock in the feature-branch versions of `backend/core/database.py`, `backend/services/blog_service.py`, and `backend/services/document_service.py`; do not let cherry-picks overwrite them.  
  - If a cherry-pick touches those files, prefer `--strategy-option ours` and manually reapply only the needed snippets (e.g., new logging).  
  - Verify `/api/v1/documents` contract matches `tests/test_contents_editor_normalize.py` after the Redis-only changes.
3. **Frontend/Auth Resolution**  
  - Reconcile `frontend/src/lib/api.ts` vs new `frontend/src/lib/api-server.ts`: client code must only call the server wrapper, while server components use the new helper to enforce cookies.  
  - Update `frontend/src/actions/auth.ts` to surface 24h session config (check `SESSION_EXPIRE_SECONDS` constant) and ensure `logout` invalidates refresh tokens server-side.  
  - In `dashboard/generate` + `settings` pages, wrap API fetches with try/catch that redirects to `/login` on 401; add logging for 403 reproduction noted in observation logs.
4. **403 / 401 Regression Tests**  
  - Reproduce the failure: `pnpm dev` + `make s` (backend) and capture failing call stack; confirm 403 originates from backend `sessions` router (likely missing auth cookies).  
  - Inspect backend logs for `Failed to create session: {"detail":"Not authenticated"}`; ensure dependency injection supplies `current_user` when establishing long-lived sessions.  
  - After fixes, repeat scenario (generate blog, navigate to settings) to verify warnings disappear; keep screenshots or log excerpts for PR notes.
5. **Dependency Audit Execution**  
  - Run `poetry show --tree | grep -E "(chroma|chainlit|langchain)"` to confirm removals, then regenerate lockfile.  
  - Validate Docker image by running `docker build -f docker/Dockerfile .` to ensure no missing wheels after cleanup.  
  - Update `docs/ARCHITECTURE.md` and `README.md` sections titled "Vector Store" / "Chainlit" to state "Removed in Nov 2025".
6. **Documentation & Tracking**  
  - Add progress updates to `docs/audit/AUTONOMOUS-WORKER-INSTRUCTIONS-v2.md` under the auth/Next.js hybrid plan.  
  - Append troubleshooting outcomes to `docs/audit/AUTH-FIX-COMPLETE-SUMMARY.md` if new auth fixes are considered part of Phase 9.  
  - Capture any lingering risk (e.g., `make s` exit codes) in `PROGRESS-TRACKER.md` under "Blockers" to maintain visibility.

## Supporting References
- Branch context & conflict inventory: `PROGRESS-TRACKER.md` (Section "Branch Sync Issue").
- Auth remediation summary: `docs/audit/AUTH-FIX-COMPLETE-SUMMARY.md`.
- Autonomous worker guidance: `docs/audit/AUTONOMOUS-WORKER-INSTRUCTIONS-v2.md` (for hybrid Next.js/audit strategy).
- Chainlit cleanup source commit: `main` @ `c3cda8a`.

## Notes & Risks
- Re-introducing deleted `src/` files will resurrect Chainlit—double-check `git status` after conflict resolution.
- Longer session TTL must match frontend expectation; clear cookies between manual tests to avoid stale tokens.
- Removing heavy deps changes Docker image size; rebuild base image before deployment.
- Keep track of `make s` failures referenced earlier (exit codes 2/130) to ensure they are addressed post-merge (likely due to auth failures).

## Context Reset Prompt (for new sessions)
If you open a fresh conversation, paste the snippet below so the assistant can rehydrate the plan quickly:

```text
You are helping me continue work on the blog-creator-agent repo.
- Branch: copilot/update-progress-tracker
- Strategy: abort the stalled rebase and cherry-pick only targeted fixes from main (auth TTL, generate page styling, dependency cleanup) while preserving the feature branch backend/blog/document services.
- Chainlit/Chroma must remain removed (Redis-only persistence).
- Reference docs/plans/20251127-1200_merge_cleanup_plan.md for the active remediation checklist.
Please confirm once you have reloaded the plan and current git status.
```
