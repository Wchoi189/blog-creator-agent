---
:type: "implementation_plan"
:category: "development"
:status: "active"
:version: "1.0"
:tags: ['implementation', 'plan', 'development']
:title: "Starter: Debug Sprint for Streamlit Analysis"
:date: "2025-11-04 21:16 (KST)"
---

# Starter: Debug Sprint for Streamlit Analysis

## Master Prompt
You are an autonomous AI agent executing a time-boxed debug sprint to stabilize the Streamlit Analysis and Advanced Analysis pages. Focus on the immediate goal and stop when the Stop Condition is met.

## Overview
- Problem summary: Upload feedback unclear; nested component validation spam; Analysis charts empty due to experiment validation
- Scope (in): Schema defaults, ExperimentStorage sanitation, page UX signals
- Scope (out): New features beyond visual feedback and sanitation
- Timebox: 5 days

## Assumptions & Constraints
- Pydantic V2 constraints remain strict
- Streamlit session_state keys unchanged
- Data location stable (`outputs/experiments/` and uploaded CSVs)

## Goal-Execute-Update Loop
- 🎯 Goal: Restore reliable rendering and charts across both pages
- NEXT TASK: Implement `default: Any` in `ComponentSchema` and retest
- Outcome Handling: Record logs before/after for validation spam
- Blueprint Update: Move to sanitation if successful

## Day-by-Day Plan
- Day 1–2: Reproduce and fix schema default typing
  - Repro: open Advanced Analysis; observe nested errors in logs
  - Fix: change `default` typing; retest visibility and logs
- Day 3–4: Sanitize `processing_time` in ExperimentStorage
  - Clamp negatives to 0.0; log clamped count; retest experiments
- Day 5: Consolidation & PR
  - Unit tests, smoke tests; author PR and change notes

## Stop Condition (Exit Criteria)
- No nested default validation warnings
- Advanced Analysis charts render after upload
- Analysis charts render for previously failing experiments

## Risks & Mitigations
- Broader negative fields → Extend sanitation narrowly with tests
- Hidden dependencies on default typing → add renderer-side fallback if needed

## Verification Checklist
- [ ] New failing test for negative `processing_time`
- [ ] Fix passes and removes log spam
- [ ] Smoke tests on both pages

## Handoff Notes
- Branch / PR: (to be filled)
- How to run tests: `pytest` + manual Streamlit check
- Open questions: Any experiments still failing validation?

---

*Use for rapid stabilization with explicit exit criteria.*
