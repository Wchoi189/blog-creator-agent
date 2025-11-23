---
type: "template"
category: "reference"
status: "active"
version: "1.0"
tags: ['template', 'reference', 'guidelines']
title: "Blueprint Template: Lightweight Debug Sprint"
date: "2025-11-04 21:10 (KST)"
---

# Blueprint Template: Lightweight Debug Sprint

## Master Prompt
You are an autonomous AI agent executing a time-boxed debug sprint. Focus on the immediate goal and stop when the Stop Condition is met.

## Overview
- Problem summary:
- Scope (in/out):
- Timebox: (e.g., 2–5 days)

## Assumptions & Constraints
- Known assumptions:
- Constraints (env, data, access):

## Goal-Execute-Update Loop
- 🎯 Goal:
- NEXT TASK:
- Outcome Handling: (pass/fail notes)
- Blueprint Update: (what changed)

## Day-by-Day Plan
- Day 1–2: Discovery & Reproduction
  - Repro steps:
  - Logs/telemetry to capture:
- Day 3–4: Hypothesis & Fix Trials
  - Hypotheses list:
  - Trial tasks (small, reversible):
- Day 5: Consolidation & PR
  - Finalize fix and tests:
  - Draft PR and change notes:

## Stop Condition (Exit Criteria)
- Repro scenario(s) pass in CI and locally
- No critical regressions surfaced
- Stakeholder acceptance for scope

## Risks & Mitigations
- Risk:
- Mitigation:

## Verification Checklist
- [ ] Failing test added (red)
- [ ] Fix implemented (green)
- [ ] Regressions tested
- [ ] Logs/metrics reviewed

## Handoff Notes
- Branch / PR:
- How to run tests:
- Open questions:

---

*Use for small, time-limited debugging efforts with explicit exit criteria.*
