---
type: "assessment"
category: "evaluation"
status: "active"
version: "1.0"
tags: ['assessment', 'evaluation', 'analysis']
title: "Streamlit Analysis & Advanced Analysis Audit"
date: "2025-11-04 03:12 (KST)"
---

# Streamlit Analysis & Advanced Analysis Audit

## Purpose

Audit the Analysis and Advanced Analysis pages to trace end-to-end dataflow, diagnose upload/render failures, and propose concrete fixes to restore full functionality.

## Scope

- **Pages**: `Analysis`, `Advanced_Analysis`
- **Engine**: Schema engine (renderers, conditional logic, data binding)
- **Data**: Experiments (JSON), enriched CSV (`outputs/experiments/enriched_constrained.csv`)
- **Evidence**: Code references, error logs (`logs/streamlit/grammar_correction_app_8501.err`)

## System Dataflow (End-to-End)

### Page bootstrap

```1:21:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/pages/3_Analysis.py
"""
Analysis Page
"""

from schema_engine import (
    SchemaLoader,
    SchemaProcessor,
    initialize_session_state,
    load_data_for_schema,
)

# Initialize session state
initialize_session_state()

# Load data
load_data_for_schema()

# Process page schema
loader = SchemaLoader()
processor = SchemaProcessor(schema_loader=loader)
processor.process_page("pages/analysis.yaml")
```

```1:21:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/pages/4_Advanced_Analysis.py
"""
Advanced Analysis Page
"""

from schema_engine import (
    SchemaLoader,
    SchemaProcessor,
    initialize_session_state,
    load_data_for_schema,
)

# Initialize session state
initialize_session_state()

# Load data
load_data_for_schema()

# Process page schema
loader = SchemaLoader()
processor = SchemaProcessor(schema_loader=loader)
processor.process_page("pages/advanced_analysis.yaml")
```

### Schema function registration (data sources + loaders)

```559:686:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/utils/utilities.py
    safe_register_data_source(
        "get_available_experiments",
        get_available_experiments,
        {"cache": True, "ttl": 60, "max_size": 20},
    )
    ...
    safe_register_loader("get_experiment_dataframe", get_experiment_dataframe)
    safe_register_loader("count_dataframe_rows", count_dataframe_rows)
    safe_register_loader("get_dataframe_columns", get_dataframe_columns)
```

### Analysis page schema (selectors → metrics → table → chart)

```10:67:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/page_schemas/pages/analysis.yaml
sections:
  - id: experiment_selection
    components:
      - type: selectbox
        key: experiment_selector
        options_source: "get_available_experiments()"
      - type: checkbox
        key: multi_compare
      - type: multiselect
        key: comparison_experiments
        options_source: "get_comparison_experiment_options()"
        visible_when: { field: multi_compare, value: true }

  - id: single_experiment_analysis
    visible_when: { field: multi_compare, value: false }
    components:
      - type: metric_columns
        key: overview_metrics
      - type: data_table
        key: performance_metrics_table
        data_source: "format_performance_metrics_table"
      - type: chart
        key: performance_chart
        chart_type: "bar"
        data_source: "format_performance_chart_data"
```

### Advanced Analysis schema (radio → select/upload → dataframe → charts)

```11:44:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/page_schemas/pages/advanced_analysis.yaml
- id: data_source_selection
  components:
    - type: radio
      key: advanced_data_source
      options: ["Experiment Results", "Upload CSV"]
      default: "Experiment Results"
    - type: selectbox
      key: advanced_experiment_selector
      visible_when: { field: advanced_data_source, value: "Experiment Results" }
    - type: file_uploader
      key: advanced_csv_upload
      visible_when: { field: advanced_data_source, value: "Upload CSV" }
```

### Conditional visibility (supports `operator: not_empty`)

```232:241:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/core/conditional_logic.py
        elif rule.operator == "is_not_empty" or rule.operator == "not_empty":
            if isinstance(field_value, list | tuple | str):
                return len(field_value) > 0
            else:
                return bool(field_value)
```

### File upload → session_state → dataframe resolution

```36:44:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/renderers/input/file_uploader.py
        return st.file_uploader(
            label=label,
            type=accepted_types,
            key=key,
            help=help_text,
            disabled=disabled,
            accept_multiple_files=accept_multiple_files,
            **filtered_kwargs,
        )
```

```380:421:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/utils/utilities.py
    uploaded = st.session_state.get("advanced_csv_upload")
    if uploaded is not None:
        content = uploaded.getvalue() if hasattr(uploaded, "getvalue") else uploaded.read()
        if content:
            df = pd.read_csv(io.BytesIO(content)) or utf-8-sig fallback
            # Alias text columns if needed
            if "err_sentence" not in df.columns and "original" in df.columns:
                df["err_sentence"] = df["original"]
            if "cor_sentence" not in df.columns and "corrected" in df.columns:
                df["cor_sentence"] = df["corrected"]
            return df
```

### Enriched CSV columns (OK for advanced visualizations)

```1:1:/workspaces/upstage-prompt-hack-a-thon-dev/outputs/experiments/enriched_constrained.csv
id,err_sentence,cor_sentence,confidence,processing_time,tokens_used,success,changes_made,original_target_part,golden_target_part,type,error_types
```

## Findings

### 1) Advanced Analysis upload “no response” is mostly UX + validation noise

- Functionally, upload works when radio = “Upload CSV”; resolver ingests `UploadedFile`, parses DataFrame, and aliases columns. However:
  - There is no immediate success indicator; feedback is only visible via downstream metrics/charts.
  - High-frequency schema validation warnings for nested components (see Finding 3) create the impression of a broken page.

### 2) Analysis charts fail due to strict Pydantic validation of experiments

- Experiments are loaded and validated as `ExperimentResult`.
```163:206:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/utils/experiment_storage.py
result = ExperimentResult.model_validate(data)
```
- Each `CorrectionResult.processing_time` requires `ge=0.0`.
```124:128:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/models/experiment.py
processing_time: float = Field(
    default=0.0,
    ge=0.0,
    description="Time taken to process this correction in seconds",
)
```
- Logs show many experiments failing validation on tiny negative microseconds (float underflow), leading to “no results data” and empty charts.

### 3) Repeated validation errors for multiselect defaults in nested layouts

- Errors: `default.str` / `default.int` receiving `[]` (list) for multiselect.
- Cause: `ComponentSchema.default` is typed as `str | int | None`; multiselect uses a list default (`[]`).
```20:31:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/models/schema.py
    options: list[str] | list[dict[str, str]] | None = Field(default=None)
    default: str | int | None = Field(default=None)
```
- Where it’s triggered:
```45:61:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/renderers/layout/nested.py
component_schema = ComponentSchema(
    type=component_def.get("type"),
    key=component_def.get("key") or f"{component_def.get('type','component')}_auto",
    ...,
    default=component_def.get("default"),
)
```
- Impact: Spammy warnings, fallback rendering paths, and occasional skipped nested content. This degrades the Advanced Analysis experience.

## Recommendations

### High Priority

1. Fix schema model to accept multiselect defaults
   - Change `ComponentSchema.default` to a permissive type (e.g., `Any`).
   - Rationale: Eliminates validation spam and stabilizes nested UI rendering.

2. Sanitize experiment results during load
   - Clamp `processing_time = max(processing_time, 0.0)` before `ExperimentResult.model_validate(data)` in `ExperimentStorage`.
   - Rationale: Keeps model constraints strict while allowing legacy/float-noise experiments to load, restoring charts.

### Medium Priority

3. Improve Advanced Analysis upload UX
   - Add immediate feedback (e.g., metric/markdown using `count_dataframe_rows`) after upload.
   - Optional: Add a radio option “Enriched CSV” that auto-loads `outputs/experiments/enriched_constrained.csv`.

## Implementation Plan

### Phase 1 – Stabilize Rendering (today)

- [ ] Update `ComponentSchema.default: Any` in `streamlit_app/schema_engine/models/schema.py`.
- [ ] Retest Advanced Analysis to confirm nested warnings disappear and controls render reliably.

### Phase 2 – Restore Analysis charts (today)

- [ ] In `ExperimentStorage._load_new_format(...)` (pre-validate), sanitize `processing_time` across results.
- [ ] Reopen failing experiments; verify metrics/table/chart render.

### Phase 3 – UX Enhancements (tomorrow)

- [ ] Add small success text/metric under Advanced Analysis “Data Overview” referencing `count_dataframe_rows`.
- [ ] Optional: Add “Enriched CSV” data source with a fixed path binding.

## Verification Steps

- Advanced Analysis
  - Set radio = “Upload CSV”; upload `outputs/experiments/enriched_constrained.csv`.
  - Expect: immediate non-zero “Total Records”, charts visible under selected category.

- Analysis
  - Select previously failing experiment; confirm performance table + bar chart display.
  - Ensure error log no longer shows `processing_time` validation failures.

## Risks / Follow-ups

- Other fields (e.g., `tokens_used`) might show edge-case negatives in some legacy data; extend sanitation if observed.
- If legacy CSV + metadata lacks required fields, `_migrate_legacy_format` may need small adjustments.

## Appendix: Key Code Anchors

```1:21:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/pages/3_Analysis.py
```
```1:21:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/pages/4_Advanced_Analysis.py
```
```10:67:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/page_schemas/pages/analysis.yaml
```
```11:44:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/page_schemas/pages/advanced_analysis.yaml
```
```559:686:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/utils/utilities.py
```
```232:241:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/core/conditional_logic.py
```
```36:44:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/renderers/input/file_uploader.py
```
```380:421:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/utils/utilities.py
```
```20:31:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/models/schema.py
```
```45:61:/workspaces/upstage-prompt-hack-a-thon-dev/streamlit_app/schema_engine/renderers/layout/nested.py
```

---

*Prepared by AI Agent — audit focused on restoring functionality and reducing error noise.*
