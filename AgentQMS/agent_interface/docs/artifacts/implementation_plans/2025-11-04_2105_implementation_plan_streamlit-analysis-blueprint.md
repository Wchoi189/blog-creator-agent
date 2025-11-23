---
type: "implementation_plan"
category: "development"
status: "active"
version: "1.0"
tags: ['implementation', 'plan', 'development']
title: "Blueprint: Fix Analysis & Advanced Analysis Errors"
date: "2025-11-04 21:05 (KST)"
---

# Blueprint: Fix Analysis & Advanced Analysis Errors

## Overview

Convert the audit findings into a living blueprint to investigate, debug, and fix: (1) Advanced Analysis upload/visibility issues and (2) Analysis page empty charts due to experiment validation failures.

## Objectives

- [ ] Eliminate nested component validation errors (multiselect defaults) and stabilize rendering
- [ ] Sanitize legacy experiment records to pass Pydantic validation and restore charts
- [ ] Improve Advanced Analysis upload UX with immediate data feedback

## Implementation Steps

### Phase 1: Rendering & Validation Stabilization (Week 1)
- [ ] Task 1.1: Fix schema default typing for multiselect
  - Update `streamlit_app/schema_engine/models/schema.py` to set `default: Any`
  - Retest Advanced Analysis; confirm nested warnings gone
  - Verify `filter_columns` and `viz_category` render correctly
- [ ] Task 1.2: Add clear upload feedback in Advanced Analysis
  - Add small metric/markdown tied to `count_dataframe_rows`
  - Verify feedback updates right after upload

### Phase 2: Experiment Data Sanitation (Week 1)
- [ ] Task 2.1: Sanitize `processing_time` in `ExperimentStorage`
  - Clamp negatives to 0.0 before `ExperimentResult.model_validate`
  - Log number of clamped rows for transparency
  - Load several failing experiments; confirm successful validation
- [ ] Task 2.2: Unblock Analysis charts
  - Verify metrics table and performance charts render
  - Ensure "no results data" messages disappear

### Phase 3: UX & Reliability Enhancements (Week 2)
- [ ] Task 3.1: Optional data source for Enriched CSV
  - Extend Advanced Analysis radio with “Enriched CSV”
  - Bind to `outputs/experiments/enriched_constrained.csv`
  - Confirm immediate charts without manual upload
- [ ] Task 3.2: Error surfacing improvements
  - Show concise banner when experiment validation fails
  - Link to logs and remediation instructions

## Success Criteria

- [ ] No recurring `ComponentSchema` default validation warnings
- [ ] Advanced Analysis: upload shows non-zero record count and charts render
- [ ] Analysis: tables and charts render for formerly failing experiments

## Risks & Mitigation

### Risk 1
- **Risk**: Additional legacy fields may violate constraints (e.g., `tokens_used`)
- **Mitigation**: Extend sanitation rules narrowly as observed; keep strict model

### Risk 2
- **Risk**: Changing `default` typing could mask other schema issues
- **Mitigation**: Add unit tests for common component defaults (multiselect, selectbox)

## Timeline

- **Start Date**: 2025-11-04
- **Target Completion**: 2025-11-11
- **Estimated Duration**: X days/weeks

## Resources Required

- Resource 1
- Resource 2

## Next Steps

1. Implement `default: Any` in `ComponentSchema`, retest Advanced Analysis
2. Add upload feedback metric/markdown; verify live update
3. Implement `processing_time` sanitation and re-open failing experiments

---

*This implementation plan follows the project's standardized format for development planning.*
