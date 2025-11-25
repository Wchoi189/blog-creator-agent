---
title: "Dashboard upload Browse button does nothing"
type: bug
date: 2025-11-24 23:45 (KST)
branch: main
status: open
severity: high
tags:
  - frontend
  - dashboard
  - upload
---

## Summary
On `/dashboard/upload`, clicking the “Browse Files” button never opens the system file picker, so documents cannot be selected through the UI.

## Environment
- Frontend dev server via `make stack` (Next.js 14.2.33)
- Browser: Chrome (devtools shows no console errors)
- Backend/Redis already running from the same stack command

## Steps to Reproduce
1. Start the stack: `make stack` (ensures backend + Next dev server on port 3002).
2. Register or log in (e.g., `longpass-user@example.com`).
3. Navigate to `http://localhost:3002/dashboard/upload`.
4. Click the “Browse Files” button or anywhere inside the drop zone.

## Expected Behavior
Browser should open a native file selection dialog tied to the hidden `<input type="file">`.

## Actual Behavior
Click has no visible effect; file picker never opens, no files are added to the list, and there are no console/server errors.

## Notes / Hypotheses
- DOM currently renders only a `<button>` without a linked `<input>`; code changes that rely on `fileInputRef` may not be packaged or hot-reloaded.
- Needs investigation to confirm whether the hidden input is missing entirely or if event wiring fails post-refresh.

## Attachments
- URL: `http://localhost:3002/dashboard/upload`
- HTML snippet observed:
  ```
  <button type="button" class="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 cursor-pointer transition">Browse Files</button>
  ```

