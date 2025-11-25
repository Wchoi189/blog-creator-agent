---
title: "Datestamp template stuck on January"
type: bug
date: 2025-11-24 23:01 (KST)
branch: main
status: fixed
severity: medium
tags:
  - docs
  - changelog
  - datestamp
---

## Summary
CHANGELOG entries inherited a static sample date (2025-01-15), so new entries appeared stale even when authored later in the year.

## Root Cause
The guideline example hard-coded the placeholder date and format, so contributors copy-pasted it verbatim instead of inserting fresh timestamps.

## Fix
Documented the required `YYYY-MM-DD HH:MM (KST)` format in `CHANGELOG.md` and updated the example entry to use a live Asia/Seoul timestamp so future changes derive the correct value.

## Verification
Manual inspection of `CHANGELOG.md` shows the new guidance and sample date; no tooling emits the stale value anymore.
