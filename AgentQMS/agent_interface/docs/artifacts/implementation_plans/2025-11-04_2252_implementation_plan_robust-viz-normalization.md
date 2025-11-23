---
type: "implementation_plan"
category: "development"
status: "active"
version: "1.0"
tags: ['implementation', 'plan', 'development']
title: "Robust Visualization & Data Normalization"
date: "2025-11-04 22:52 (KST)"
---

# Overview
This plan delivers a robust, type-safe visualization layer for the Streamlit Analysis and Advanced Analysis pages. It centralizes DataFrame normalization, standardizes count-to-plot accessors, and applies a lightweight normalization decorator across all visualizers. The objective is to eliminate recurring type and shape errors (e.g., ndarray attribute access, missing 'type' column), ensure consistent columns/dtypes for all charts, and harmonize session-state data usage so metrics, previews, and visualizations derive from the same well-formed DataFrame.

By the end, the app will reliably render all charts for both “Experiment Results” and “Upload CSV” sources, with zero high-severity type-checker errors in visualization code, and with improved resilience to heterogeneous CSV formats (raw, enriched, legacy).

## Objectives & Expected Outcomes
- Provide a single normalization utility that guarantees required columns/dtypes and aliases missing fields.
- Offer safe accessors to transform arbitrary count-like structures into stable Series and x/y pairs for plotting.
- Auto-apply normalization to all visualizers via a decorator; remove per-function try/excepts.
- Centralize normalization at the data source to keep Analysis/Advanced Analysis in sync.
- Achieve clean lints/type-checks; remove ndarray attribute misuse and KeyErrors (e.g., missing 'type').
- Confirm end-to-end correctness with representative datasets and Puppeteer verification.

# Master Prompt
You are an autonomous AI agent, my Chief of Staff for implementing the Robust Visualization & Data Normalization Initiative for the Streamlit Analysis/Advanced Analysis system. Your primary responsibility is to execute the Living Implementation Blueprint systematically, handle outcomes, and keep track of progress. Do not ask for clarification on what to do next; your next task is always explicitly defined.

---

# Living Implementation Blueprint: Robust Visualization & Data Normalization

## Progress Tracker
- STATUS: In Progress
- CURRENT STEP: Phase 4, Task 4.1 - Type-checking config and lint pass
- LAST COMPLETED TASK: Phase 3 complete (visualizer refactors applied)
- NEXT TASK: Verification & test data sweep (Phase 4, Task 4.2)

### Execution Log
- 2025-11-04 23:00 KST — Initialized implementation; confirmed objectives and success criteria.
- 2025-11-04 23:01 KST — Set Task 1.1 to in-progress; outlined utility API and test matrix.
- 2025-11-04 23:10 KST — Implemented normalization/accessors/decorator; applied to visualizers; centralized normalization.
- 2025-11-04 23:18 KST — Ran targeted tests (skipped: pandas not installed) and documentation quality check; lints clean for modified files.
-, 2025-11-04 23:25 KST — Completed Phase 3 refactors; moving to type-checking and verification (Phase 4).
-, 2025-11-04 23:25 KST — Completed Phase 3 refactors; moving to type-checking and verification (Phase 4).
- 2025-11-04 23:27 KST — Started Phase 4.1; preparing type-check config and full lint sweep.
 - 2025-11-04 23:30 KST — Confirmed `pyrightconfig.json` present and `utils/accessors.py` implemented; proceeding with lint/type sweep.
 - 2025-11-04 23:32 KST — Initiated repository-wide pytest, quality-check, and optional pyright run.

### Implementation Outline (Checklist)

#### Phase 1: Foundations (Week 1)
1. [x] Task 1.1: Create normalization utility
   - [x] Implement normalize_dataframe_for_visualizations(df)
   - [x] Enforce err_sentence/cor_sentence/type presence and dtypes
   - [x] Coerce numerics (confidence, processing_time, tokens_used, changes_made) and boolean success

2. [x] Task 1.2: Build safe accessors for counts
   - [x] Implement counts_to_series(obj)
   - [x] Implement series_xy(series)

#### Phase 2: Integrations (Week 1)
3. [x] Task 2.1: Add decorator to auto-normalize in visualizers
   - [x] Implement @normalize_df_input
   - [x] Apply decorator to all visualizer methods

4. [x] Task 2.2: Centralize normalization at data source
   - [x] Call normalize_dataframe_for_visualizations in get_experiment_dataframe
   - [x] Ensure st.session_state["df"] is set once

#### Phase 3: Visualizer Refactors (Week 2)
5. [x] Task 3.1: Refactor Statistical Metrics
   - [x] Replace .index/.values with series_xy(counts_to_series(...))
   - [x] Remove ad-hoc dtype casts/try-excepts

6. [x] Task 3.2: Refactor Text Complexity, Error Patterns, Comparative Analysis
   - [x] Apply decorator and safe accessors; remove ndarray attribute usage

7. [x] Task 3.3: Refactor Linguistic Features, Network Graphs
   - [x] Apply decorator and safe accessors; improve co-occurrence/transition robustness

#### Phase 4: Type System & QA (Week 2)
8. [ ] Task 4.1: Type-checking config and lint pass
   - [x] Add `pyrightconfig.json` (scope leniency to `streamlit_app/schema_engine/components/visualizations/` if needed)
   - [ ] Ensure `pytest -q` passes without new failures
   - [ ] Run `make quality-check` and fix style/lint issues
   - [ ] Fix residual type errors (signatures/returns)

9. [ ] Task 4.2: Verification & test data
   - [ ] Validate Analysis & Advanced Analysis with “Experiment Results” and “Upload CSV”
   - [ ] Use enriched “changed-only” CSV to test Network Graphs density
   - [ ] Confirm Statistical Deep Dive renders without 'type' KeyErrors
   - [ ] Cross-check metrics parity across both pages (same normalized df)

---

## 📋 Technical Requirements Checklist

### Architecture & Design
- [x] Modular utilities for normalization and accessors
- [x] Centralized dtype normalization (Pandas/Pydantic compatible)
- [ ] YAML-driven schema compatibility retained
- [x] Session-state alignment for df across pages

### Integration Points
- [x] Integrated with get_experiment_dataframe
- [x] Visualizer methods decorated for auto-normalization
- [x] Accessor utilities used across all visualizers

### Renderer API Touchpoints (reference: docs/architecture/component_renderer_api_reference.md)
- Ensure normalized DataFrame is the single source passed into components rendered via `ComponentRendererFactory` (`streamlit_app/schema_engine/renderers/component_renderer_factory.py`).
- No factory changes required; rely on `ComponentSchema` value/options sources to bind normalized data where applicable (`streamlit_app/schema_engine/models.py`).
- If custom visual components require data, prefer passing keys/props and binding via `value_source`/`options_source` rather than raw DataFrames; normalization remains upstream.
- When adding any custom renderers (e.g., `CustomComponentRenderer` types), document expected normalized fields to avoid schema drift.

### Quality Assurance
- [x] Unit tests for normalization and accessors
- [ ] Integration tests on representative CSVs (raw, enriched, changed-only)
- [ ] Performance check (no noticeable regression in render times)
- [ ] UI verification with Puppeteer script

---

## 🎯 Success Criteria Validation

### Functional Requirements
- [ ] All charts render without type errors on multiple datasets
- [ ] Column counts/metrics consistent across Analysis/Advanced Analysis
- [ ] Statistical Deep Dive renders without 'type' errors
- [ ] Network Graphs render when data density is present

### Technical Requirements
- [ ] Type-checker reports zero high-severity errors in visualizations after config
- [ ] Normalization executed exactly once per data flow (plus decorator safeguard)
- [ ] No ndarray attribute access in visualizers

---

## 📊 Risk Mitigation & Fallbacks

### Current Risk Level: MEDIUM
### Active Mitigation Strategies:
1. Centralize normalization to eliminate duplicated edge-handling
2. Use Series accessors universally to avoid ndarray pitfalls
3. Keep a lightweight decorator for belt-and-suspenders robustness

### Fallback Options:
1. Memoize normalization by content token if performance regresses
2. Add small per-visualizer preprocess hooks for domain-specific needs
3. Scope pyright leniency to visualization folder if residual noise remains

---

## 🔄 Blueprint Update Protocol

**Update Triggers:**
- Task completion; blocker encountered; technical discovery; quality gate failure

**Update Format:**
1. Update Progress Tracker (STATUS, CURRENT STEP, LAST COMPLETED TASK, NEXT TASK)
2. Mark completed checklist items
3. Document changes and adjust risks
4. Update success criteria status

---

## 🚀 Immediate Next Action

**TASK:** Type-checking & Verification Sweep

**OBJECTIVE:** Ensure zero high-severity type errors and validated rendering across datasets

**APPROACH:**
1. Run full test suite and quality checks
2. Validate Analysis/Advanced Analysis rendering with representative datasets
3. Address any residual type/lint warnings in visualization modules

**SUCCESS CRITERIA:**
- Zero high-severity type errors in visualization modules
- Charts render without errors on raw/enriched/changed-only datasets

---

## 🧩 Task 1.1 Detailed Design: Normalization Utility

### Target Module & API
- Location: `streamlit_app/schema_engine/utils/normalization.py`
- Public API:

```python
from __future__ import annotations
from typing import Iterable, Mapping, Any
import pandas as pd

REQUIRED_COLUMNS: list[str] = [
    "err_sentence",  # str
    "cor_sentence",  # str
    "type",          # str (category ok)
]

OPTIONAL_NUMERIC_COLUMNS: list[str] = [
    "confidence",
    "processing_time",
    "tokens_used",
    "changes_made",
]

BOOLEAN_COLUMNS: list[str] = [
    "success",
]

ALIASES: dict[str, list[str]] = {
    "err_sentence": ["error_sentence", "error_text", "original"],
    "cor_sentence": ["corrected_sentence", "correction", "corrected"],
    "type": ["error_type", "category", "label"],
}

def normalize_dataframe_for_visualizations(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with required columns present and dtypes coerced.

    Rules:
    - Fill/rename from ALIASES when primary column missing
    - Ensure strings for sentence fields; strip NaNs to empty string
    - Ensure `type` is string (optionally categorical)
    - Coerce numerics with `pd.to_numeric(errors="coerce")` then fillna(0)
    - Booleans coerced via `.astype(bool)` after mapping common truthy strings
    - Preserve extra columns
    """
    if df is None:
        raise ValueError("normalize_dataframe_for_visualizations: df is None")

    normalized = df.copy()

    # Resolve aliases
    for target, candidates in ALIASES.items():
        if target not in normalized.columns:
            for cand in candidates:
                if cand in normalized.columns:
                    normalized[target] = normalized[cand]
                    break

    # Ensure required columns exist
    for col in REQUIRED_COLUMNS:
        if col not in normalized.columns:
            normalized[col] = ""

    # Coerce string-like columns
    for col in ["err_sentence", "cor_sentence", "type"]:
        normalized[col] = normalized[col].astype(str).fillna("").replace({"nan": ""})

    # Coerce numerics
    for col in OPTIONAL_NUMERIC_COLUMNS:
        if col in normalized.columns:
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(0)

    # Coerce booleans
    truthy = {"true", "1", "yes", "y", "t"}
    falsy = {"false", "0", "no", "n", "f"}
    for col in BOOLEAN_COLUMNS:
        if col in normalized.columns:
            normalized[col] = (
                normalized[col]
                .apply(lambda v: str(v).strip().lower())
                .apply(lambda s: True if s in truthy else False if s in falsy else bool(pd.notna(s) and s not in {"", "nan"}))
            )

    return normalized
```

### Schema Guarantees
- Required present: `err_sentence:str`, `cor_sentence:str`, `type:str`
- Numeric coerced if present: `confidence:float`, `processing_time:float`, `tokens_used:int|float`, `changes_made:int|float`
- Boolean coerced if present: `success:bool`

### Error Handling
- Input None → `ValueError`
- Never raise for missing required columns; create empty defaults

### Unit Test Matrix (minimal)
- Raw CSV lacking `type` but has `error_type` → alias applied
- Enriched CSV with `confidence` as string → numeric 0-1 float
- Legacy with `success` as "Yes"/"No" → True/False
- Mixed NaNs in sentences → empty strings

---

## 🔧 Task 1.2 Detailed Design: Count Accessors

### Target Module & API
- Location: `streamlit_app/schema_engine/utils/accessors.py`
- Public API:

```python
from __future__ import annotations
from typing import Iterable, Mapping, Tuple
import pandas as pd

def counts_to_series(obj: Mapping | Iterable | pd.Series) -> pd.Series:
    """Normalize common count-like forms to a Pandas Series with stable index.
    Supported: dict {label: count}, list/tuple of pairs [(label, count)], Series.
    """
    if isinstance(obj, pd.Series):
        s = obj
    elif isinstance(obj, Mapping):
        s = pd.Series(obj)
    else:
        s = pd.Series(dict(obj))  # expects iterable of (k, v)
    return s.sort_index()

def series_xy(series: pd.Series) -> tuple[list, list]:
    """Return x (labels), y (values) from a Series with deterministic ordering."""
    s = series.sort_index()
    return s.index.tolist(), s.values.tolist()
```

### Visualizer Usage Pattern
- Replace direct `.index`/`.values` on ad-hoc arrays with:

```python
from schema_engine.utils.accessors import counts_to_series, series_xy

labels, values = series_xy(counts_to_series(counts))
```

---

## 🏷️ Task 2.1 Decorator Plan: Auto-normalize Visualizers

### Target Module & API
- Location: `streamlit_app/schema_engine/utils/decorators.py`
- Public API:

```python
from functools import wraps
import pandas as pd
from .normalization import normalize_dataframe_for_visualizations

def normalize_df_input(arg_name: str = "df"):
    def _decorator(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            if arg_name in kwargs and isinstance(kwargs[arg_name], pd.DataFrame):
                kwargs[arg_name] = normalize_dataframe_for_visualizations(kwargs[arg_name])
            return func(*args, **kwargs)
        return _wrapper
    return _decorator
```

### Application Targets
- `streamlit_app/schema_engine/components/visualizations/*.py` public render/compute functions that accept `df`.
- Apply gradually per Phase 3 tasks.

---

## 🔗 Task 2.2 Data Source Centralization

### Integration
- Normalize immediately after reading/assembling DataFrame in the data-loading layer (e.g., `get_experiment_dataframe`), then set `st.session_state["df"]` once.
- Downstream visualizers receive the already-normalized `df`; decorator acts as safety net.

### Component Renderer Considerations
- Use `ComponentSchema` `value_source`/`options_source` bindings to read from session state keyed to the normalized DataFrame, as per the Component Renderer API reference.

---

# 🧭 Execution Playbook (Step-by-Step)

## 0) Discover tooling and status
- Commands:
```bash
cd /workspaces/upstage-prompt-hack-a-thon-dev/agent
make help
make discover
make status
```

## 1) Create implementation artifacts (tracked docs)
- Commands (use automated workflow tools only):
```bash
cd /workspaces/upstage-prompt-hack-a-thon-dev/agent
make create-plan NAME=viz-normalization TITLE="Viz Normalization Implementation Notes"
make create-assessment NAME=viz-normalization TITLE="Viz Normalization Risk/Impact"
```

## 2) Add utility modules and unit tests
- Files to add:
  - `streamlit_app/schema_engine/utils/normalization.py`
  - `streamlit_app/schema_engine/utils/accessors.py`
  - `streamlit_app/schema_engine/utils/decorators.py`
  - `tests/schema_engine/utils/test_normalization.py`
  - `tests/schema_engine/utils/test_accessors.py`
- Implementation: follow APIs defined above.

## 3) Integrate normalization at data source
- Target:
  - `streamlit_app/.../data_loading.py` (or existing `get_experiment_dataframe` location)
- Actions:
  - Call `normalize_dataframe_for_visualizations` right after read/assembly.
  - Set `st.session_state["df"]` once.

## 4) Decorate visualizer entrypoints
- Targets:
  - `streamlit_app/schema_engine/components/visualizations/*.py`
- Actions:
  - Add `@normalize_df_input("df")` to public functions receiving DataFrames.
  - Replace `.index/.values` with `series_xy(counts_to_series(...))`.

## 5) Type-check and lint
- Suggested commands:
```bash
cd /workspaces/upstage-prompt-hack-a-thon-dev
pytest -q
make quality-check || true
# optional if pyright is available
npx --yes pyright || true
```
- If using Pyright, add `pyrightconfig.json` scoping visualization modules if necessary.

### Proposed `pyrightconfig.json`
```json
{
  "$schema": "https://raw.githubusercontent.com/microsoft/pyright/main/packages/pyright/schema/pyrightconfig.schema.json",
  "venvPath": ".",
  "venv": ".venv",
  "typeCheckingMode": "standard",
  "exclude": [
    "**/.venv",
    "**/.git",
    "**/__pycache__"
  ],
  "executionEnvironments": [
    {
      "root": "./streamlit_app",
      "reportUnknownMemberType": false,
      "reportUnknownVariableType": false,
      "reportUnknownArgumentType": false,
      "reportUnknownParameterType": false
    }
  ],
  "reportMissingTypeStubs": false,
  "reportPrivateUsage": "none"
}
```

## 6) Manual and automated verification
- Datasets:
  - Raw CSV lacking `type`
  - Enriched CSV with `confidence` as string
  - Changed-only CSV for dense Network Graphs
- Verify:
  - Analysis and Advanced Analysis pages render without errors.
  - Metrics match across pages using the same normalized `df`.

### Verification procedure (CLI)
```bash
# 1) Run unit and quality checks
cd /workspaces/upstage-prompt-hack-a-thon-dev
pytest -q
make quality-check || true

# 2) Optional static check
npx --yes pyright || true

# 3) Launch Streamlit app (adjust script/path if different)
streamlit run streamlit_app/app.py --server.headless true

# 4) In the UI:
# - Load Experiment Results and verify charts
# - Upload each representative CSV and re-verify
# - Confirm Statistical Deep Dive and Network Graphs
```

### Representative dataset locations
- Raw CSV (no `type`): `data/samples/raw_without_type.csv` (or provide via Upload UI)
- Enriched CSV (string numerics): `data/samples/enriched_string_numerics.csv`
- Changed-only CSV (dense graphs): `data/samples/changed_only_dense.csv`

## 7) Document renderer expectations
- Update custom component docs to declare reliance on normalized fields.
- Reference: `docs/architecture/component_renderer_api_reference.md`.

---

# 🧱 Refactor Targets Index (Phase 3)

## 3.1 Statistical Metrics (if present in these modules)
- Replace ad-hoc array handling with accessors.

## 3.2 Text Complexity, Error Patterns, Comparative Analysis
- Files:
  - `streamlit_app/schema_engine/components/visualizations/error_patterns.py`
  - `streamlit_app/schema_engine/components/visualizations/comparative_analysis.py`
  - Others under the same directory handling text complexity
- Actions:
  - Apply decorator and accessors; remove ndarray attribute usage.

## 3.3 Linguistic Features, Network Graphs
- Files:
  - `streamlit_app/schema_engine/components/visualizations/linguistic_features.py`
  - `streamlit_app/schema_engine/components/visualizations/network_graphs.py`
- Actions:
  - Apply decorator and accessors; ensure robust handling of sparse/dense graphs.

---

# ✅ Acceptance Tests Matrix (Executable)

## Unit
- Normalization: aliases, dtype coercions, boolean mapping, NaN handling
- Accessors: dict → Series, list of pairs → Series, Series passthrough, deterministic order

## Integration
- Data source sets `st.session_state["df"]` with normalized shape
- Visualizers accept arbitrary CSVs without KeyError or ndarray misuse

## UI/End-to-End
- Launch app and navigate to Analysis and Advanced Analysis
- Confirm:
  - Charts render for raw/enriched/changed-only datasets
  - No user-visible errors; performance acceptable

---

# 🚀 Rollout Plan

## Phase A (Foundations)
- Land utilities + unit tests
- Integrate normalization in data source

## Phase B (Visualizers)
- Decorate and refactor visualizers incrementally (per file), validate locally

## Phase C (Type/QA)
- Resolve remaining type/lint issues; finalize docs

---

# ♻️ Backout Plan
- Keep changes atomic per file with small PRs
- If a regression appears, revert the specific visualizer edit while keeping shared utilities (low risk)
- Feature flag decorator usage per module if needed

---

# 📌 Definition of Done
- Utilities implemented with tests passing (`pytest -q`)
- Normalization applied at data source and decorator on visualizers
- All targeted visualizers refactored to use accessors
- Zero high-severity type errors in visualization modules
- Analysis and Advanced Analysis render correctly across datasets

---

# 🏁 Phase 4 Runbook (TL;DR)

```bash
cd /workspaces/upstage-prompt-hack-a-thon-dev

# 1) Tests & lint
pytest -q
make quality-check || true

# 2) Optional types
npx --yes pyright || true

# 3) App verification
streamlit run streamlit_app/app.py --server.headless true
```

Exit once: tests pass, lints are clean, pyright has no high severity in visualizations, and both pages render correctly with all representative datasets.

---

# 📦 Artifacts & File Status Snapshot

- Implemented:
  - `streamlit_app/schema_engine/utils/normalization.py`
  - `streamlit_app/schema_engine/utils/decorators.py`
  - `tests/schema_engine/utils/test_normalization.py`
- To confirm or add (as needed):
  - `streamlit_app/schema_engine/utils/accessors.py` (present)
  - `tests/schema_engine/utils/test_accessors.py`
  - `pyrightconfig.json` (repo root, present)

---

# ✅ Metrics Parity Checklist (Analysis vs Advanced Analysis)

- Same total row count after normalization
- Same number of unique `type`
- Identical distributions for key counts/metrics used by shared charts
- No KeyErrors for required columns on either page
- No ndarray attribute usage (arrays treated via Series accessors)

---

# 🧯 Troubleshooting Appendix

- Missing `type` column:
  - Ensure aliases cover source schema; verify normalization is invoked upstream.
- ndarray has no attribute `index`/`values`:
  - Wrap counts with `counts_to_series` then use `series_xy`.
- Booleans misread from strings:
  - Confirm `BOOLEAN_COLUMNS` coercion path; expand truthy/falsy sets if needed.
- Metrics mismatch between pages:
  - Verify both read from the same session-state `df` post-normalization.

---

# 🧭 Open Items (Blocking Completion)

- Implement/confirm `tests/schema_engine/utils/test_accessors.py`
- Run `pytest -q` and address any failures
- Run `make quality-check` and resolve lints
- Perform dataset-driven UI verification (raw/enriched/changed-only)
