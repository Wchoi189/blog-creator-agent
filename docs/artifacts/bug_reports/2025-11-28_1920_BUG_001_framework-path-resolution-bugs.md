---
type: "bug_report"
category: "troubleshooting"
status: "active"
severity: "high"
version: "1.0"
tags: ['bug', 'issue', 'troubleshooting']
title: "Path Resolution and Naming Convention Bugs in AgentQMS Framework"
date: "2025-11-28 19:20 (KST)"
---

# Bug Report: Path Resolution and Naming Convention Bugs in AgentQMS Framework

## Bug ID
BUG-001

<!-- REQUIRED: Fill these sections when creating the initial bug report -->
## Summary
Multiple path resolution and naming convention issues in AgentQMS framework scripts prevent proper execution when run from interface directory, and cause validation failures for generated artifacts.

## Environment
- **OS**: Linux
- **Python Version**: 3.11+
- **Dependencies**: AgentQMS framework components
- **Browser**: N/A

## Steps to Reproduce
1. Run `make validate` from `AgentQMS/interface/` directory
2. Observe FileNotFoundError for artifacts directory
3. Run `make create-plan` from `AgentQMS/interface/` directory  
4. Observe index update failure due to incorrect script path
5. Run `make create-bug-report` from `AgentQMS/interface/` directory
6. Observe validation failure due to naming convention mismatch

## Expected Behavior
- All make commands should execute successfully from interface directory
- Artifact validation should pass for framework-generated artifacts
- Path resolution should work correctly regardless of execution context

## Actual Behavior
- `make validate` fails with "No such file or directory: 'artifacts'"
- `make create-plan` fails to update indexes due to missing script path
- Bug reports fail validation due to incorrect filename pattern and invalid status

## Error Messages
```
FileNotFoundError: [Errno 2] No such file or directory: 'artifacts'
❌ Error updating indexes: /path/to/python: can't open file 'update_artifact_indexes.py': [Errno 2] No such file or directory
❌ Artifact validation failed: Missing valid file type prefix / Invalid status 'open'
```

## Root Cause Analysis

### Issue 1: Path Resolution in validate_artifacts.py
- **Location**: `AgentQMS/agent_tools/compliance/validate_artifacts.py:__init__`
- **Problem**: Default `artifacts_root="artifacts"` is relative but not resolved to project root
- **Impact**: Scripts fail when run from subdirectories

### Issue 2: Incorrect Index Updater Path
- **Location**: `AgentQMS/agent_tools/core/artifact_workflow.py:update_indexes`
- **Problem**: Path points to `../agent_tools/documentation/` but script is in `../toolkit/documentation/`
- **Impact**: Index updates fail silently

### Issue 3: Path Resolution in update_artifact_indexes.py
- **Location**: `AgentQMS/toolkit/documentation/update_artifact_indexes.py:__init__`
- **Problem**: Default `artifacts_root="docs/artifacts"` not resolved to project root
- **Impact**: Fails when run from interface directory

### Issue 4: Bug Report Naming Convention Mismatch
- **Location**: `AgentQMS/toolkit/core/artifact_templates.py:bug_report.filename_pattern`
- **Problem**: Pattern `"BUG_YYYY-MM-DD_HHMM_NNN_{name}.md"` puts prefix before timestamp
- **Impact**: Validator expects timestamp first, then prefix

### Issue 5: Invalid Default Status for Bug Reports
- **Location**: `AgentQMS/toolkit/core/artifact_templates.py:bug_report.frontmatter.status`
- **Problem**: Status set to `"open"` but validator only accepts predefined statuses
- **Impact**: Validation fails for generated bug reports

## Impact
- **Severity**: High
- **Affected Users**: All users of AgentQMS framework interface commands
- **Workaround**: Run scripts from project root directory (temporary)

## Proposed Fixes

### Fix 1: Resolve Relative Paths in Validators
```python
# In validate_artifacts.py and update_artifact_indexes.py
if not artifacts_root_path.is_absolute():
    artifacts_root_path = get_project_root() / artifacts_root_path
```

### Fix 2: Correct Index Updater Path
```python
# In artifact_workflow.py
path = Path(__file__).parent.parent.parent / "toolkit" / "documentation" / "update_artifact_indexes.py"
```

### Fix 3: Update Bug Report Filename Pattern
```python
# In artifact_templates.py
"filename_pattern": "YYYY-MM-DD_HHMM_BUG_NNN_{name}.md"
```

### Fix 4: Use Valid Status for Bug Reports
```python
# In artifact_templates.py
"status": "active"
```

## Screenshots/Logs
N/A - Console output shows error messages clearly.

## Testing
- All fixes applied and tested successfully
- `make validate`, `make compliance`, `make create-plan`, `make create-bug-report` now work correctly
- Generated artifacts pass validation
- Index updates function properly

<!-- OPTIONAL: Resolution sections - fill these during investigation and fixing -->
## Investigation

### Root Cause Analysis
- **Cause**: What is causing the issue
- **Location**: Where in the code
- **Trigger**: What triggers the issue

### Related Issues
- Related issue 1
- Related issue 2

## Proposed Solution

### Fix Strategy
How to fix the issue.

### Implementation Plan
1. Step 1
2. Step 2

### Testing Plan
How to test the fix.

## Status
- [ ] Confirmed
- [ ] Investigating
- [ ] Fix in progress
- [ ] Fixed
- [ ] Verified

## Assignee
Who is working on this bug.

## Priority
High/Medium/Low (urgency for fixing, separate from severity above)

---

*This bug report follows the project's standardized format for issue tracking.*