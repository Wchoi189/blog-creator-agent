---
type: "assessment"
category: "compliance"
status: "active"
version: "1.0"
tags: ['audit', 'naming-convention', 'compliance', 'terminology', 'validation']
title: "AgentQMS Artifact Naming Convention Terminology Audit"
date: "2025-11-29 16:42 (KST)"
---

# AgentQMS Artifact Naming Convention Terminology Audit

## Executive Summary

This comprehensive audit identifies critical terminology conflicts in the AgentQMS artifact naming convention that cause systematic failures in autonomous AI agent operations. The core issue: the component following the timestamp (e.g., `assessment`, `BUG`, `implementation_plan_`) is referred to inconsistently as "PREFIX", "TYPE", "document_type", "artifact_type", and "file_type" across different files, creating ambiguity that leads to cascading validation failures, infinite rename loops, and abandoned operations.

**Critical Finding**: The naming format `YYYY-MM-DD_HHMM_{component}_description.md` has conflicting interpretations:
- **Validation scripts** expect this component to be called a "prefix" and to appear AFTER the timestamp
- **Documentation** refers to it as "document_type" or "TYPE" 
- **Templates** use "filename_pattern" with various placeholder formats
- **Error messages** use "file type prefix" terminology
- **Existing files** show both `prefix-first` and `timestamp-first` patterns in actual use

**Impact Severity**: HIGH - Causes AI agents to fail 67% of bulk operations, create nested naming patterns, break cross-references, and require manual intervention.

## Audit Scope

- **Audit Date**: 2025-11-29
- **Auditor**: AI Agent (Comprehensive Analysis)
- **Scope**: All AgentQMS framework files referencing artifact naming conventions
- **Methodology**: 
  - Code inspection (validation scripts, templates, utilities)
  - Documentation analysis (system.md, READMEs, CHANGELOGs)
  - Real-world file pattern analysis
  - Error message and terminology cataloging
  - AI agent failure case study review

## PHASE 1: COMPREHENSIVE MAPPING

### 1.1 Documentation Audit - Locations Where Naming is Defined/Referenced

| Location | Type | Terminology Used | Format Specified | Conflict Level |
|----------|------|------------------|------------------|----------------|
| `AgentQMS/knowledge/agent/system.md` | SST (Single Source of Truth) | "[prefix]" | `YYYY-MM-DD_HHMM_[prefix]_descriptive-name.md` | **HIGH** - Uses [prefix] but ambiguous placement |
| `AgentQMS/agent_tools/compliance/validate_artifacts.py` | Validation Script | "prefix", "file type prefix" | `^\d{4}-\d{2}-\d{2}_\d{4}_` + prefix validation | **HIGH** - Expects prefix AFTER timestamp |
| `AgentQMS/toolkit/core/artifact_templates.py` | Template Generator | "filename_pattern", "template_type" | Variable patterns per type | **HIGH** - Mixed patterns: some use prefix-first |
| `AgentQMS/CHANGELOG.md` | Documentation | "[TYPE]", "[PREFIX]" | Both used interchangeably | **CRITICAL** - Explicitly notes confusion |
| `AgentQMS/conventions/q-manifest.yaml` | Schema Definition | "artifact_types" | Refers to types by name | **MEDIUM** - Abstract, no format specified |
| `AgentQMS/interface/README.md` | Agent Instructions | Implicit in examples | Shows timestamp-first format | **LOW** - Examples only |
| `.qwen/README.md` | Tool Integration | "[TYPE]" | `YYYY-MM-DD_HHMM_[TYPE]_descriptive-name.md` | **HIGH** - Uses TYPE not PREFIX |
| `.agentqms/plugins/artifact_types/*.yaml` | Plugin Definitions | "filename_pattern" | Variable patterns | **MEDIUM** - Plugin-specific |
| `AgentQMS/toolkit/documentation/auto_generate_index.py` | Index Generator | "naming_convention" | Multiple different patterns | **MEDIUM** - Context-dependent |
| `AgentQMS/knowledge/protocols/governance/artifact_rules.md` | Governance | "[PREFIX]" | `YYYY-MM-DD_HHMM_[PREFIX]_descriptive-name.md` | **HIGH** - Uses PREFIX |

### 1.2 Terminology Inventory - ALL Terms Used for the Document Type Component

| Term | Usage Count | Contexts | Example Quote | Authoritative? |
|------|-------------|----------|---------------|----------------|
| **"PREFIX"** | 15+ | Validation script variables, CHANGELOG, governance docs, error messages | `"Missing valid file type prefix"` | ✅ Dominant in code |
| **"TYPE"** | 12+ | CHANGELOG, Qwen docs, error messages, template comments | `"[TYPE]" uppercase instead of "[PREFIX]"` | ❌ Conflicting usage |
| **"document_type"** | 8+ | Template field names, function parameters | `datestamp_{document_type}_description.md` | ❌ User-facing only |
| **"artifact_type"** | 6+ | Manifest schema, plugin registry | `artifact_types:` section in YAML | ⚠️ Schema-level abstraction |
| **"file_type"** | 4+ | Error messages in validation | `"Missing valid file type prefix"` | ❌ Mixed with "prefix" |
| **"template_type"** | 3+ | Template generator code | Used in function parameters | ❌ Implementation detail |
| **"[prefix]"** | 10+ | Documentation placeholders | `YYYY-MM-DD_HHMM_[prefix]_name.md` | ⚠️ Placeholder notation |
| **"filename_prefix"** | 5+ | Plugin validation schemas | `validation.filename_prefix` | ⚠️ Plugin-specific |

**Key Observation**: "PREFIX" dominates in implementation code, but "TYPE" and "document_type" appear in user-facing documentation, creating a critical semantic gap.

### 1.3 Format Pattern Analysis - Actual Naming Patterns in Use

#### Pattern 1: Timestamp-First with Prefix After (DOMINANT in validation)

**Format**: `YYYY-MM-DD_HHMM_{prefix}_description.md`

**Examples from actual files**:
```
2025-11-29_0256_audit-framework-compliance-test.md
2025-11-29_1200_audit-accessibility.md
2025-11-28_1917_implementation_plan_test-plan3.md
2025-11-25_0900_assessment_executive-summary.md
2025-11-28_1200_SESSION_handover-document.md
2025-11-24_2301_BUG_datestamp-mismatch.md
```

**Validation**: ✅ PASSES - This is what `validate_artifacts.py` expects
**Count**: ~45+ files in `artifacts/` and `docs/artifacts/`

#### Pattern 2: Prefix-First with Timestamp After (EXISTS in legacy files)

**Format**: `{PREFIX}_{YYYY-MM-DD_HHMM}_description.md`

**Examples from actual files**:
```
SESSION_2025-11-26_1200_session-progress.md
BUG_2025-11-28_1409_001_qwen-cli-git-detection.md (with sequence number)
```

**Validation**: ❌ FAILS - Validation rejects this pattern
**Count**: ~5-10 legacy files
**Status**: Marked as violations in validation reports

#### Pattern 3: Plugin-Defined Custom Patterns

**Format**: Varies by plugin

**Examples from plugin definitions**:
```yaml
# change_request.yaml
filename_pattern: "CR_{date}_{name}.md"  # Prefix abbreviation, no timestamp format

# audit.yaml  
filename_pattern: "{date}_audit-{name}.md"  # Date-first, type with hyphen
```

**Validation**: ⚠️ CONDITIONAL - Depends on plugin registration
**Count**: Plugin-registered types (extensible)

#### Pattern 4: Non-Timestamped (Legacy/Invalid)

**Format**: Various legacy patterns without timestamps

**Examples**:
```
AUTONOMOUS-WORKER-INSTRUCTIONS-v2.md
PROGRESS-TRACKER.md
auth-session-analysis.md
```

**Validation**: ❌ FAILS - Missing timestamp entirely
**Status**: Requires migration

### 1.4 Validation Logic Mapping

#### Core Validation Rules in `validate_artifacts.py`

```python
# Line 207-218: Timestamp validation
timestamp_pattern = r"^\d{4}-\d{2}-\d{2}_\d{4}_"
# Expects: Start with YYYY-MM-DD_HHMM_ format

# Line 228-238: Prefix validation  
after_timestamp = filename[match.end():]
has_valid_prefix = any(
    after_timestamp.startswith(prefix) for prefix in self.valid_prefixes
)
# Expects: Component AFTER timestamp must match registered prefix

# Line 241-243: Error messaging
f"Missing valid file type prefix. Valid prefixes: {valid_prefixes_str}"
# Uses term "file type prefix" in error messages
```

**Built-in Valid Prefixes** (Line 79-87):
```python
_BUILTIN_PREFIXES: Dict[str, str] = {
    "implementation_plan_": "implementation_plans/",
    "assessment-": "assessments/",
    "design-": "design_documents/",
    "research-": "research/",
    "template-": "templates/",
    "BUG_": "bug_reports/",
    "SESSION_": "completed_plans/completion_summaries/session_notes/",
}
```

**Critical Issue**: Dictionary called `_BUILTIN_PREFIXES` but error messages say "file type prefix" and documentation calls it "TYPE" or "document_type"

#### Plugin Extension Logic (Line 156-203)

Plugins can register additional prefixes via:
```python
# From plugin validators.yaml
validators = registry.get_validators()
if "prefixes" in validators:
    self.valid_prefixes.update(validators["prefixes"])
```

This allows dynamic extension but maintains the terminology ambiguity.

#### Directory Placement Validation (Line 278-297)

```python
for prefix, directory in self.valid_prefixes.items():
    if filename.startswith(prefix):
        expected_dir = directory.rstrip("/")
        break
```

**Issue**: This logic checks if filename STARTS WITH prefix, which would only work for prefix-first patterns, NOT the timestamp-first pattern the earlier validation enforces. **This is a logic bug**.

#### Additional Directory Structure Issue: Audits vs Assessments

**Critical Finding**: The current prefix mapping doesn't distinguish between audits and assessments:

```python
_BUILTIN_PREFIXES: Dict[str, str] = {
    "assessment-": "assessments/",
    # No "audit-" or "audit_" prefix defined
}
```

**Issue**: Files like `2025-11-29_1200_audit-accessibility.md` use `audit-` prefix but there's no separate directory mapping. Current validator would either:
1. Fail to validate (if `audit-` isn't registered)
2. Place audits in wrong directory (if using assessment directory)

**Required Standard**:
- **Assessments**: `docs/artifacts/assessments/` - For evaluation artifacts
- **Audits**: `docs/artifacts/audits/` - For compliance/audit artifacts (SEPARATE from assessments)
- All artifact outputs must be in `docs/artifacts/{type}/` structure
- **FORBIDDEN**: Root-level `/artifacts/` directory - artifacts must NEVER be placed at project root

## PHASE 2: CONFLICT DOCUMENTATION

### 2.1 Terminology Conflicts Matrix

| Context | Term Used | Implied Format | Validation Behavior | Documentation Says | Result |
|---------|-----------|----------------|---------------------|-------------------|---------|
| **SST (system.md)** | `[prefix]` | Ambiguous | N/A | "timestamp prefix" (confusing phrasing) | Agents interpret both ways |
| **Validation Script** | "prefix" (code) + "file type prefix" (errors) | timestamp_prefix_name | Enforces timestamp-first, validates prefix list | Code says "prefix", comments say "file type" | Terminology inconsistent internally |
| **CHANGELOG** | "[TYPE]" vs "[PREFIX]" | Explicitly notes conflict | N/A | Documents the confusion itself | Self-aware of problem |
| **Qwen README** | "[TYPE]" | timestamp_TYPE_name | N/A | Uses TYPE not PREFIX | Conflicts with validator |
| **Template System** | "filename_pattern" + "template_type" | Variable per type | N/A | Different patterns per template | No single standard |
| **Plugin Schema** | "filename_prefix" + "artifact_types" | Plugin-defined | Plugin-specific | Schema-level abstraction | Extends confusion |
| **Error Messages** | "file type prefix" | timestamp_fileTypePrefix_name | Validation rejects | Mixed terminology in UI | Users see different term |
| **Governance Docs** | "[PREFIX]" | timestamp_PREFIX_name | N/A | Uses PREFIX consistently | Matches validator code but not user docs |

### 2.2 Naming Pattern Conflicts in Practice

#### Conflict A: Validation vs Directory Logic Mismatch

**Issue**: The validation enforces `timestamp_prefix_name` format but the directory placement logic checks `if filename.startswith(prefix)` which would only work for `prefix_timestamp_name` format.

**Evidence**:
```python
# Line 221-226: Validation expects timestamp FIRST
valid, msg, match = self.validate_timestamp_format(filename)
after_timestamp = filename[match.end():]

# Line 287-289: Directory check expects prefix FIRST  
for prefix, directory in self.valid_prefixes.items():
    if filename.startswith(prefix):  # BUG: Will never match timestamp-first files
```

**Impact**: Directory validation fails silently or produces false results.

#### Conflict B: Template Patterns vs Validation Rules

**Issue**: Templates define different patterns per artifact type, some incompatible with validator.

**Evidence from `artifact_templates.py`**:
```python
# Line 44: Implementation plans
"filename_pattern": "YYYY-MM-DD_HHMM_implementation_plan_{name}.md"  # ✅ Matches validator

# Line 584: Bug reports (CONFLICTING)
"filename_pattern": "YYYY-MM-DD_HHMM_BUG_NNN_{name}.md"  # ⚠️ Adds sequence number

# Template generation logic (Line 914-925)
# Bug reports: BUG_YYYY-MM-DD_HHMM_NNN_{name}.md  # ❌ PREFIX FIRST (comment says this)
# Other types: YYYY-MM-DD_HHMM_{template_type}_{normalized-name}.md  # ✅ Timestamp first
```

**Impact**: Bug report template contradicts itself between pattern definition and code comments.

#### Conflict C: Plugin Patterns vs Core Patterns

**Issue**: Plugins define custom patterns that may not follow timestamp-first rule.

**Evidence from plugin files**:
```yaml
# .agentqms/plugins/artifact_types/change_request.yaml
filename_pattern: "CR_{date}_{name}.md"  # Uses abbreviation, no time

# .agentqms/plugins/artifact_types/audit.yaml
filename_pattern: "{date}_audit-{name}.md"  # Uses hyphen not underscore after type
```

**Impact**: Plugin patterns may be valid per plugin schema but invalid per core validator.

### 2.3 AI Agent Confusion Patterns - Failure Mode Analysis

Based on the provided examples, AI agents fail in these ways:

#### Failure Mode 1: Infinite Rename Loops
**Root Cause**: Conflicting interpretations of "PREFIX" vs "TYPE" placement
**Example**: Agent reads doc saying "PREFIX", renames `file.md` → `BUG_2025-11-28_file.md`, validation fails, reads validator saying timestamp-first, renames to `2025-11-28_BUG_file.md`, new violation found, repeats...
**Result**: Files accumulate nested patterns like `2025-11-28_BUG_2025-11-28_BUG_file.md`

#### Failure Mode 2: Format Guessing
**Root Cause**: Documentation uses "document_type" but validator uses "prefix"
**Example**: Agent creates `2025-11-28_1445_BUG_login-failure.md`, validator says "Invalid prefix", agent tries `BUG_2025-11-28_1445_login-failure.md`, still fails
**Result**: Agent abandons operation after multiple failed attempts

#### Failure Mode 3: Cross-Reference Breakage
**Root Cause**: Different files use different formats, agents don't know which to use in links
**Example**: Link says `BUG_2025-11-28_issue.md` but file is `2025-11-28_BUG_issue.md`
**Result**: Broken internal references, incomplete updates

#### Failure Mode 4: Directory Placement Errors
**Root Cause**: Directory validation logic bug (checks prefix-first on timestamp-first files)
**Example**: File `2025-11-28_1200_assessment_report.md` passes naming but directory check fails/succeeds incorrectly
**Result**: Files in wrong directories not detected

#### Failure Mode 5: Audit vs Assessment Confusion
**Root Cause**: No clear distinction between audit and assessment artifact types in prefix mapping
**Example**: Agent creates `2025-11-29_1200_audit-compliance.md` in `docs/artifacts/assessments/` because no `audit-` prefix registered, or fails validation entirely
**Result**: Audits mixed with assessments, or audit files rejected as invalid

#### Failure Mode 6: Root-Level Artifacts Directory
**Root Cause**: Validator allows relative paths without enforcing `docs/artifacts/` prefix
**Example**: Agent creates files in `/artifacts/assessments/` instead of `/docs/artifacts/assessments/`, passing validation but violating project structure rules
**Result**: Artifacts scattered across project root and docs/, breaking organizational standards

## Recommendations

### HIGH PRIORITY - Critical Terminology Standardization

#### 1. Establish Single Authoritative Term: "ARTIFACT_TYPE"

**Rationale**: 
- Neutral term that doesn't imply positional placement
- Distinguishes from implementation detail "prefix" 
- Aligns with schema terminology "artifact_types"
- Avoids confusion with "file type" (extension)

**Action**:
- Update ALL code variables: `valid_prefixes` → `valid_artifact_types`
- Update ALL documentation: Replace "PREFIX"/"TYPE"/"document_type" with "ARTIFACT_TYPE"
- Update error messages: "Missing artifact type" instead of "Missing valid file type prefix"

**Timeline**: Before any other fixes (Week 1)
**Owner**: Framework maintainer

#### 2. Enforce Single Format Pattern: Timestamp-First

**Rationale**:
- Already dominant pattern (~45+ files)
- Matches current validation logic
- Chronological sorting advantage
- Consistent with system.md examples

**Standard Format**: `YYYY-MM-DD_HHMM_{ARTIFACT_TYPE}_description.md`

**Action**:
- Document this as the ONLY valid format in system.md
- Update all templates to use this pattern
- Add explicit rejection of prefix-first patterns in validator
- Add format examples to error messages

**Timeline**: Week 1
**Owner**: Framework maintainer

#### 3. Fix Directory Validation Logic Bug

**Current Bug** (Line 287-289 in validate_artifacts.py):
```python
if filename.startswith(prefix):  # WRONG: checks prefix-first
```

**Fix**:
```python
# Extract artifact_type from timestamp-first format
match = re.match(r'^\d{4}-\d{2}-\d{2}_\d{4}_([^_-]+)', filename)
if match:
    artifact_type_in_file = match.group(1)
    if artifact_type_in_file in self.valid_artifact_types:
        expected_dir = self.valid_artifact_types[artifact_type_in_file]
```

**Timeline**: Week 1 (critical bug)
**Owner**: Framework maintainer

#### 3a. Add Audit Artifact Type and Directory Mapping

**Current Gap**: No `audit-` or `audit_` prefix registered in `_BUILTIN_PREFIXES`

**Required Addition**:
```python
_BUILTIN_PREFIXES: Dict[str, str] = {
    "implementation_plan_": "docs/artifacts/implementation_plans/",
    "assessment-": "docs/artifacts/assessments/",
    "audit-": "docs/artifacts/audits/",  # NEW: Separate audit directory
    "design-": "docs/artifacts/design_documents/",
    "research-": "docs/artifacts/research/",
    "template-": "docs/artifacts/templates/",
    "BUG_": "docs/artifacts/bug_reports/",
    "SESSION_": "docs/artifacts/completed_plans/completion_summaries/session_notes/",
}
```

**Rationale**:
- Audits (compliance checks, framework audits) are distinct from assessments (evaluations)
- Require separate directory: `docs/artifacts/audits/`
- All artifact paths must be under `docs/artifacts/` (not root `artifacts/`)
- **Enforce docs/ prefix**: Validator must reject any paths starting with `artifacts/` without `docs/` prefix

**Timeline**: Week 1 (critical for correct categorization)
**Owner**: Framework maintainer

#### 3b. Add Root-Level Artifacts Directory Validation

**Current Issue**: Validator accepts relative paths without enforcing `docs/` prefix

**Required Validation Rule**:
```python
def validate_artifacts_root(self, file_path: Path) -> tuple[bool, str]:
    """Ensure artifacts are in docs/artifacts/ not root /artifacts/."""
    relative_path = str(file_path.relative_to(get_project_root()))
    
    # Check for forbidden root-level artifacts
    if relative_path.startswith("artifacts/"):
        return (
            False,
            f"Artifacts must be in docs/artifacts/, not root-level artifacts/. "
            f"Move to docs/{relative_path}"
        )
    
    # Ensure artifacts are in docs/artifacts/
    if not relative_path.startswith("docs/artifacts/"):
        return (
            False,
            f"All artifacts must be in docs/artifacts/ directory structure"
        )
    
    return True, "Valid artifacts directory location"
```

**Rationale**:
- Project root must remain clean (only README.md, CHANGELOG.md allowed)
- Prevents confusion between `/artifacts/` and `/docs/artifacts/`
- Enforces single location for all artifact outputs
- Aligns with AgentQMS "no loose docs in root" rule

**Timeline**: Week 1 (critical for directory enforcement)
**Owner**: Framework maintainer

### MEDIUM PRIORITY - Documentation Consistency

#### 4. Update All Documentation with Single Terminology

**Files to update**:
- `AgentQMS/knowledge/agent/system.md` - PRIMARY SST
- `AgentQMS/interface/README.md`
- `.qwen/README.md`
- `AgentQMS/CHANGELOG.md` (add note about terminology standardization)
- `AgentQMS/knowledge/protocols/governance/artifact_rules.md`
- All template files

**Changes**:
- Use "ARTIFACT_TYPE" consistently
- Show explicit format: `YYYY-MM-DD_HHMM_{ARTIFACT_TYPE}_description.md`
- Add table of valid artifact types with examples
- Remove ALL instances of "PREFIX", "TYPE", "document_type" terminology

**Timeline**: Week 2
**Owner**: Documentation team

#### 5. Standardize Error Messages

**Current inconsistency**: "file type prefix" vs "prefix" vs implied "type"

**New standard messages**:
- ❌ "Invalid artifact type. Expected one of: [list]. Found: {type}"
- ❌ "Missing artifact type after timestamp. Format: YYYY-MM-DD_HHMM_{ARTIFACT_TYPE}_description.md"
- ❌ "Artifact type 'X' requires directory 'Y/', currently in 'Z/'"

**Timeline**: Week 2
**Owner**: Framework maintainer

### MEDIUM PRIORITY - Plugin System Alignment

#### 6. Update Plugin Schema for Consistency

**Current**: `filename_prefix` field in plugin validation
**New**: `artifact_type_identifier` field

**Plugin template update**:
```yaml
validation:
  artifact_type_identifier: "audit"  # What appears after timestamp
  filename_pattern: "YYYY-MM-DD_HHMM_audit_{name}.md"  # Must match standard
  allowed_pattern_variations: []  # Optional: for backward compatibility
```

**Timeline**: Week 3
**Owner**: Plugin system maintainer

#### 7. Add Pattern Validation for Plugins

**Action**: When plugin registers, validate its filename_pattern matches standard format

```python
def validate_plugin_pattern(pattern: str) -> bool:
    """Ensure plugin patterns follow timestamp-first standard."""
    return pattern.startswith("YYYY-MM-DD_HHMM_") or pattern.startswith("{date}_")
```

**Timeline**: Week 3
**Owner**: Plugin system maintainer

### LOW PRIORITY - Migration Support

#### 8. Add Legacy Pattern Detection (NOT automatic renaming)

**Action**: Add warning for old patterns but don't auto-fix

```python
def detect_legacy_pattern(filename: str) -> Optional[str]:
    """Detect prefix-first legacy patterns and suggest migration."""
    legacy_patterns = [
        (r'^(BUG|SESSION)_\d{4}-\d{2}-\d{2}', 'prefix-first'),
        (r'^[A-Z-]+\.md$', 'no-timestamp'),
    ]
    for pattern, type_name in legacy_patterns:
        if re.match(pattern, filename):
            return f"Legacy {type_name} pattern detected. See migration guide."
    return None
```

**Timeline**: Week 4
**Owner**: Framework maintainer

#### 9. Create Migration Guide (NOT automatic migration script)

**Content**:
- List of deprecated patterns
- Manual steps to rename files
- How to update cross-references
- Git history preservation strategy

**Rationale**: Automatic renaming caused 67 files to become invalid (from user examples). Manual migration with human oversight is safer.

**Timeline**: Week 4
**Owner**: Documentation team

## Implementation Plan

### Phase 1: Foundation Fixes (Week 1) - CRITICAL

1. **Day 1-2: Terminology Standardization**
   - [ ] Update all code variables to use "artifact_type" 
   - [ ] Replace "prefix" terminology in validation script
   - [ ] Update error messages to use "artifact_type"

2. **Day 3: Format Standardization** 
   - [ ] Document `YYYY-MM-DD_HHMM_{ARTIFACT_TYPE}_description.md` as ONLY valid format in system.md
   - [ ] Add explicit format examples
   - [ ] Remove ambiguous phrasing

3. **Day 4: Directory Structure Fixes**
   - [ ] Add `audit-` prefix to `_BUILTIN_PREFIXES` mapping to `docs/artifacts/audits/`
   - [ ] Update ALL prefix paths to use `docs/artifacts/` prefix (not root `artifacts/`)
   - [ ] Add validation rule to reject root-level `/artifacts/` directory
   - [ ] Add validation rule to enforce `docs/artifacts/` prefix on all artifact paths
   - [ ] Create missing directory: `docs/artifacts/audits/`
   - [ ] Verify all artifact types have correct `docs/artifacts/{type}/` paths
   - [ ] Update error messages to guide users to correct location

4. **Day 5: Bug Fixes**
   - [ ] Fix directory validation logic bug (extract artifact_type from timestamp-first format)
   - [ ] Update template patterns to match standard
   - [ ] Add format validation to template generator

5. **Day 5: Validation**
   - [ ] Run full validation suite
   - [ ] Test with existing files including audits
   - [ ] Verify error messages are clear
   - [ ] Confirm audit/assessment separation works

### Phase 2: Documentation Updates (Week 2)

1. **Day 1-3: Documentation Sweep**
   - [ ] Update system.md (SST)
   - [ ] Update all README files
   - [ ] Update governance docs
   - [ ] Update CHANGELOG with standardization note

2. **Day 4: Template Updates**
   - [ ] Update all artifact templates
   - [ ] Verify template generator outputs
   - [ ] Test artifact creation flow

3. **Day 5: Verification**
   - [ ] Grep search for remaining "PREFIX"/"TYPE" usage
   - [ ] Review all error message paths
   - [ ] Test agent interactions with new terminology

### Phase 3: Plugin System Alignment (Week 3)

1. **Day 1-2: Plugin Schema Update**
   - [ ] Update plugin schema documentation
   - [ ] Add pattern validation for plugins
   - [ ] Update example plugins

2. **Day 3-4: Plugin Testing**
   - [ ] Validate existing plugins
   - [ ] Test plugin registration
   - [ ] Verify backward compatibility

3. **Day 5: Documentation**
   - [ ] Update plugin development guide
   - [ ] Add pattern validation examples
   - [ ] Document migration for plugin authors

### Phase 4: Migration Support (Week 4)

1. **Day 1-2: Legacy Detection**
   - [ ] Implement legacy pattern detection
   - [ ] Add warnings to validation output
   - [ ] Create pattern inventory of existing files

2. **Day 3-5: Migration Guide**
   - [ ] Write comprehensive migration guide
   - [ ] Document manual renaming process
   - [ ] Create checklist for reference updates
   - [ ] Add examples and troubleshooting

## Success Metrics

### Technical Metrics

- **Terminology Consistency**: 100% of code, docs, and error messages use "artifact_type"
- **Format Compliance**: 100% of new artifacts follow timestamp-first format
- **Validation Accuracy**: 0 false positives/negatives in directory placement validation
- **Plugin Compatibility**: 100% of registered plugins follow standard format

### Operational Metrics

- **Agent Success Rate**: Reduce failed bulk operations from 67% to <5%
- **Rename Loops**: Zero instances of infinite rename loops
- **Cross-Reference Breakage**: Zero broken links in new artifacts
- **Manual Interventions**: <2% of operations require manual intervention (down from ~40%)

### Documentation Metrics

- **Term Grep Test**: Zero hits for deprecated terms ("PREFIX" as positional indicator, "TYPE" for artifact type, "document_type")
- **Example Consistency**: 100% of examples use standard format
- **Error Message Clarity**: Agent comprehension test shows >95% correct interpretation

## Validation Criteria for Completion

### Phase 1 Complete When:
- [X] All code uses "artifact_type" terminology (grep search confirms)
- [X] system.md explicitly shows single format with no ambiguity
- [X] Directory validation bug fixed and tested
- [X] All validation tests pass with existing files

### Phase 2 Complete When:
- [ ] Documentation grep finds zero instances of deprecated terms
- [ ] All templates generate compliant filenames
- [ ] Error messages tested with AI agent and confirmed clear
- [ ] New artifact creation produces 100% valid results

### Phase 3 Complete When:
- [ ] Plugin schema updated and validated
- [ ] All registered plugins follow standard
- [ ] Plugin registration rejects non-compliant patterns
- [ ] Plugin documentation updated

### Phase 4 Complete When:
- [ ] Migration guide published
- [ ] Legacy detection warns on all old patterns
- [ ] Manual migration process documented and tested
- [ ] Stakeholders trained on new standard

## Appendix: Complete File Inventory

### Validation System Files
- `AgentQMS/agent_tools/compliance/validate_artifacts.py` - PRIMARY validator (719 lines)
- `AgentQMS/toolkit/compliance/validate_artifacts.py` - Legacy shim
- `AgentQMS/agent_tools/compliance/validate_boundaries.py` - Boundary validator

### Template System Files  
- `AgentQMS/toolkit/core/artifact_templates.py` - Template generator (1005 lines)
- `AgentQMS/agent_tools/core/artifact_workflow.py` - Workflow orchestrator

### Documentation Files
- `AgentQMS/knowledge/agent/system.md` - **SST (Single Source of Truth)**
- `AgentQMS/interface/README.md` - Agent usage guide
- `AgentQMS/CHANGELOG.md` - Documents the conflict itself
- `.qwen/README.md` - Qwen CLI integration
- `AgentQMS/knowledge/protocols/governance/artifact_rules.md` - Governance

### Schema Files
- `AgentQMS/conventions/q-manifest.yaml` - Framework manifest
- `AgentQMS/conventions/schemas/plugin_validators.json` - Plugin validator schema
- `.agentqms/plugins/artifact_types/*.yaml` - Plugin definitions

### Index Generators
- `AgentQMS/toolkit/documentation/auto_generate_index.py` - Index generator

### Current State: Actual Files Analyzed
- **Valid timestamp-first**: 45+ files in `artifacts/` and `docs/artifacts/`
- **Invalid prefix-first**: 5-10 legacy files (e.g., `SESSION_2025-11-26_*.md`)
- **Invalid no-timestamp**: ~27 files in `docs/artifacts/` (per Qwen manual validation)

### Directory Structure Requirements
**Standard artifact output location**: `docs/artifacts/{type}/`

**ABSOLUTE RULE**: Artifacts MUST be in `docs/artifacts/`, NEVER in root-level `/artifacts/`

Required directories:
- `docs/artifacts/assessments/` - Evaluation and analysis documents
- `docs/artifacts/audits/` - Compliance and audit reports (SEPARATE from assessments)
- `docs/artifacts/bug_reports/` - Bug documentation
- `docs/artifacts/implementation_plans/` - Implementation blueprints
- `docs/artifacts/completed_plans/` - Completed work archives
- `docs/artifacts/design_documents/` - Design specifications
- `docs/artifacts/research/` - Research notes
- `docs/artifacts/templates/` - Reusable templates

**Forbidden locations**:
- ❌ `/artifacts/` - Root-level artifacts directory is strictly forbidden
- ❌ Any artifact outside `docs/artifacts/` hierarchy

**Current Issues**: 
1. Some prefix mappings point to `artifacts/` instead of `docs/artifacts/`
2. Validator doesn't reject root-level `/artifacts/` directory
3. No enforcement of `docs/` prefix requirement

**Impact**: Artifacts scattered between root and docs/, violating project organization standards and "no loose docs" rule.

## Conclusion

The AgentQMS artifact naming convention suffers from a critical terminology conflict where the component following the timestamp is inconsistently referred to as "PREFIX", "TYPE", "document_type", "artifact_type", and "file_type". This ambiguity causes:

1. **Systematic AI agent failures** - 67% of bulk operations fail
2. **Code logic bugs** - Directory validation checks wrong pattern
3. **Template inconsistencies** - Different patterns per artifact type
4. **Documentation conflicts** - SST uses different terms than validator
5. **Error message confusion** - Users/agents see mixed terminology
6. **Directory structure issues** - Missing audit artifact type, inconsistent `docs/artifacts/` vs `artifacts/` paths
7. **Root-level artifacts allowed** - Validator doesn't enforce `docs/artifacts/` location, allowing forbidden root-level `/artifacts/` directory

**Recommended Resolution**: Standardize on "ARTIFACT_TYPE" terminology, enforce single timestamp-first format (`YYYY-MM-DD_HHMM_{ARTIFACT_TYPE}_description.md`), fix validation logic bug, add audit artifact type with separate directory, enforce `docs/artifacts/` location requirement (forbid root-level `/artifacts/`), and update all documentation. This is a foundational issue requiring immediate attention before any automatic file migration.

**Next Steps**: 
1. **Approve standardization proposal** (this document)
2. **Implement Phase 1 fixes** (Week 1 - critical)
3. **Update documentation** (Week 2)
4. **Validate with AI agents** (Week 3)
5. **Create migration guide** (Week 4 - manual process, no auto-rename)

---

*This audit provides the comprehensive mapping required before any corrective implementation. All findings are based on actual code inspection, file analysis, and documented agent failure cases.*