---
type: "bug_report"
category: "troubleshooting"
status: "active"
severity: "medium"
version: "1.0"
tags: ['bug', 'issue', 'troubleshooting']
title: "Uppercase Validation Incorrectly Skipped for uppercase_prefix Artifact Types"
date: "2025-11-30 16:05 (KST)"
---

# Bug Report: Uppercase Validation Incorrectly Skipped for uppercase_prefix Artifact Types

## Bug ID
BUG-001

<!-- REQUIRED: Fill these sections when creating the initial bug report -->
## Summary
The ALL CAPS validation check in `validate_artifacts.py` is incorrectly skipped for artifact types with `case: "uppercase_prefix"` (such as `BUG_*` and `SESSION_*`). The validation logic contains a conditional `if expected_case != "uppercase_prefix":` that bypasses uppercase checking entirely when it should only allow uppercase in the prefix, not the descriptive part.

This allows invalid filenames like `"SESSION_ALL-CAPS.md"` to pass validation when they should fail. According to `artifact_rules.yaml`, uppercase_prefix means "prefix is uppercase, rest is lowercase" - the descriptive part after the prefix must still be lowercase.

## Environment
- **OS**: Linux
- **Python Version**: 3.x (project uses Python)
- **Dependencies**: AgentQMS framework validation tools
- **Browser**: N/A (CLI validation tool)

## Steps to Reproduce
1. Create an artifact file with an uppercase_prefix type and uppercase descriptive part:
   ```bash
   touch docs/artifacts/bug_reports/2025-11-30_1200_BUG_001_ALL-CAPS-NAME.md
   ```

2. Run artifact validation:
   ```bash
   cd AgentQMS/interface && make validate
   ```

3. Observe that the file passes validation when it should fail

4. Compare with non-uppercase_prefix types:
   ```bash
   touch docs/artifacts/assessments/2025-11-30_1200_assessment-ALL-CAPS.md
   cd AgentQMS/interface && make validate
   # This correctly fails validation
   ```

## Expected Behavior
- For `uppercase_prefix` artifact types (BUG_*, SESSION_*), the prefix should be uppercase but the descriptive part should be lowercase
- Filenames like `"BUG_001_ALL-CAPS-NAME.md"` should FAIL validation
- Filenames like `"BUG_001_lowercase-name.md"` should PASS validation
- The validation should enforce the rule from `artifact_rules.yaml`: "prefix is uppercase, rest is lowercase"

## Actual Behavior
- The uppercase validation check is completely skipped when `expected_case == "uppercase_prefix"`
- Invalid filenames like `"SESSION_ALL-CAPS.md"` incorrectly pass validation
- The descriptive part can contain ANY casing (ALL CAPS, Mixed Case, etc.) without failing
- No validation error is reported for uppercase words in the descriptive portion

## Error Messages
### Problematic Code (Lines 383-391 in validate_artifacts.py):
```python
# Check for ALL CAPS or uppercase words in descriptive part
if expected_case != "uppercase_prefix":
    if descriptive_part.isupper() or any(
        word.isupper() and len(word) > 1
        for word in descriptive_part.replace("-", "_").split("_")
    ):
        return (
            False,
            "Artifact filenames must be lowercase. No ALL CAPS allowed. Use kebab-case (lowercase with hyphens)",
        )
```

**Issue**: The condition `if expected_case != "uppercase_prefix":` causes the entire uppercase validation block to be skipped for BUG_* and SESSION_* files.

### Expected Rule from artifact_rules.yaml:
```yaml
bug_report:
  prefix: "BUG_"
  case: "uppercase_prefix"  # prefix is uppercase, rest is lowercase
  example: "2025-11-29_1800_BUG_login-failure.md"

session_note:
  prefix: "SESSION_"
  case: "uppercase_prefix"  # prefix is uppercase, rest is lowercase
  example: "2025-11-29_1800_SESSION_sprint-review.md"
```

## Screenshots/Logs
N/A - Code logic error identified by Cursor Bugbot static analysis in post-merge review of PR#7.

## Impact
- **Severity**: Medium
- **Affected Users**: 
  - Developers creating bug reports (BUG_* files)
  - Developers creating session notes (SESSION_* files)
  - AgentQMS framework maintainers
  - Automated validation pipelines
- **Workaround**: 
  - Manual review of all BUG_* and SESSION_* filenames
  - Team discipline to follow lowercase convention in descriptive parts
  - No automated enforcement available

<!-- OPTIONAL: Resolution sections - fill these during investigation and fixing -->
## Investigation

### Root Cause Analysis
- **Cause**: Incorrect conditional logic that skips ALL uppercase validation for uppercase_prefix types
- **Location**: 
  - File: `AgentQMS/agent_tools/compliance/validate_artifacts.py`
  - Lines: 383-391 (main issue)
  - Function: `validate_naming_convention()` method
- **Trigger**: Any validation attempt on files with artifact types that have `case: "uppercase_prefix"` in their type details
- **Logic Error**: The code interprets `uppercase_prefix` as "skip all uppercase checks" when it should mean "allow uppercase prefix, but validate descriptive part is lowercase"

### Affected Artifact Types
Based on `artifact_rules.yaml`, the following types are affected:
1. **bug_report**: `BUG_*` prefix
2. **session_note**: `SESSION_*` prefix

Both types specify: `case: "uppercase_prefix"  # prefix is uppercase, rest is lowercase`

### Related Issues
- Part of dual-bug report from Cursor Bugbot post-merge analysis of PR#7
- Companion to Bug Report: `2025-11-30_1530_BUG_001_cursor-bugbot-post-merge-issues.md`
- Bug 1 (fixed): Ineffective `--include-agentqms` flag in check_links.py
- Bug 2 (this report): Uppercase validation skip in validate_artifacts.py

## Proposed Solution

### Fix Strategy
Restructure the validation logic to:
1. **Remove the skip condition** - Don't bypass validation for uppercase_prefix types
2. **Always validate descriptive part** - Check that the descriptive portion (after the prefix) is lowercase
3. **Preserve prefix handling** - Allow uppercase in the prefix portion only
4. **Improve error messages** - Provide context-specific error messages for uppercase_prefix violations

### Implementation Plan

#### Phase 1: Code Fix in validate_artifacts.py (Lines 383-391)

**Current Code (Buggy):**
```python
# Check for ALL CAPS or uppercase words in descriptive part
if expected_case != "uppercase_prefix":
    if descriptive_part.isupper() or any(
        word.isupper() and len(word) > 1
        for word in descriptive_part.replace("-", "_").split("_")
    ):
        return (
            False,
            "Artifact filenames must be lowercase. No ALL CAPS allowed. Use kebab-case (lowercase with hyphens)",
        )
```

**Proposed Fix:**
```python
# Check for ALL CAPS or uppercase words in descriptive part
# Always validate - descriptive part must be lowercase for ALL types
if descriptive_part.isupper() or any(
    word.isupper() and len(word) > 1
    for word in descriptive_part.replace("-", "_").split("_")
):
    if expected_case == "uppercase_prefix":
        return (
            False,
            "Artifact filenames with uppercase prefix must have lowercase descriptive part. "
            f"Example: BUG_001_lowercase-name.md (not BUG_001_UPPERCASE-NAME.md)",
        )
    else:
        return (
            False,
            "Artifact filenames must be lowercase. No ALL CAPS allowed. Use kebab-case (lowercase with hyphens)",
        )
```

**Changes:**
1. Remove `if expected_case != "uppercase_prefix":` condition
2. Move uppercase check outside the conditional
3. Add context-specific error message for uppercase_prefix types
4. Maintain existing error message for other types

#### Phase 2: Create Unit Tests

Create test file: `AgentQMS/agent_tools/compliance/test_validate_artifacts_uppercase.py`

**Test Cases:**
1. `test_bug_report_lowercase_descriptive_passes()` - Valid: `BUG_001_lowercase-name.md`
2. `test_bug_report_uppercase_descriptive_fails()` - Invalid: `BUG_001_ALL-CAPS.md`
3. `test_bug_report_mixed_case_descriptive_fails()` - Invalid: `BUG_001_Mixed-Case.md`
4. `test_session_note_lowercase_descriptive_passes()` - Valid: `SESSION_sprint-review.md`
5. `test_session_note_uppercase_descriptive_fails()` - Invalid: `SESSION_ALL-CAPS.md`
6. `test_assessment_uppercase_fails()` - Valid existing behavior: `assessment-ALL-CAPS.md` fails
7. `test_prefix_uppercase_allowed()` - Ensure BUG_ and SESSION_ prefixes remain uppercase

#### Phase 3: Scan Existing Artifacts

Before deploying fix, scan for existing non-compliant artifacts:
```bash
# Find BUG_ files with uppercase descriptive parts
find docs/artifacts/bug_reports -name "*BUG_*" -type f | while read f; do
  basename "$f" | grep -E 'BUG_[0-9]+_[A-Z]' && echo "Non-compliant: $f"
done

# Find SESSION_ files with uppercase descriptive parts
find docs/artifacts -name "*SESSION_*" -type f | while read f; do
  basename "$f" | grep -E 'SESSION_[A-Z]' && echo "Non-compliant: $f"
done
```

If non-compliant files found, rename them before deploying fix.

#### Phase 4: Update Documentation

1. Clarify `artifact_rules.yaml` comments if ambiguous
2. Update validation error templates if using template system
3. Document the fix in `AgentQMS/CHANGELOG.md`

#### Phase 5: Deployment & Validation

1. Deploy code fix to `validate_artifacts.py`
2. Run full test suite: `pytest AgentQMS/agent_tools/compliance/test_validate_artifacts_uppercase.py -v`
3. Run framework validation: `cd AgentQMS/interface && make validate && make compliance`
4. Verify 100% compliance rate maintained
5. Test with manual artifact creation to ensure error messages are helpful

### Testing Plan

#### Unit Tests
- Test valid uppercase_prefix filenames (lowercase descriptive part)
- Test invalid uppercase_prefix filenames (uppercase/mixed descriptive part)
- Test non-uppercase_prefix types maintain existing behavior
- Test error messages are context-appropriate

#### Integration Tests
- Run validation on all existing artifacts (should remain 100% compliant)
- Create test artifacts with various naming patterns
- Verify validation catches new violations

#### Regression Tests
- Ensure no changes to validation behavior for non-uppercase_prefix types
- Verify prefix portion can remain uppercase for BUG_* and SESSION_* files
- Confirm framework compliance rate stays at 100%

#### Manual Testing
```bash
# Test 1: Valid BUG_ file (lowercase descriptive)
touch docs/artifacts/bug_reports/2025-11-30_1200_BUG_001_test-lowercase.md
cd AgentQMS/interface && make validate
# Expected: PASS

# Test 2: Invalid BUG_ file (uppercase descriptive)
touch docs/artifacts/bug_reports/2025-11-30_1200_BUG_001_TEST-UPPERCASE.md
cd AgentQMS/interface && make validate
# Expected: FAIL with helpful error message

# Test 3: Valid SESSION_ file
touch docs/artifacts/completed_plans/completion_summaries/session_notes/2025-11-30_1200_SESSION_valid-name.md
cd AgentQMS/interface && make validate
# Expected: PASS

# Test 4: Invalid SESSION_ file
touch docs/artifacts/completed_plans/completion_summaries/session_notes/2025-11-30_1200_SESSION_INVALID-NAME.md
cd AgentQMS/interface && make validate
# Expected: FAIL with helpful error message
```

## Status
- [x] Confirmed
- [x] Investigating
- [ ] Fix in progress
- [ ] Fixed
- [ ] Verified

## Assignee
Unassigned - awaiting implementation

## Priority
Medium (affects validation accuracy but has manual workaround; no existing artifacts currently violate the rule)

---

*This bug report follows the project's standardized format for issue tracking.*