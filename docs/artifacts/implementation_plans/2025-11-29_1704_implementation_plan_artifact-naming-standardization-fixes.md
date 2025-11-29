---
type: "implementation_plan"
category: "development"
status: "active"
version: "1.0"
tags: ['implementation', 'plan', 'development']
title: "Artifact Naming Convention Standardization - Autonomous Implementation"
date: "2025-11-29 17:04 (KST)"
---

# Master Prompt

You are an autonomous AI agent implementing **AgentQMS Artifact Naming Convention Standardization**. This plan fixes critical terminology conflicts and validation bugs identified in the comprehensive audit (`2025-11-29_1642_assessment-artifact-naming-terminology-conflicts.md`). Execute tasks systematically without asking for clarification.

**Core Workflow:**
1. **Read** the current NEXT TASK
2. **Execute** the task with all specified steps
3. **Validate** results against success criteria
4. **Update** this blueprint (mark completed, set next task)
5. **Report** outcomes and move to next task

**Critical Rules:**
- Make ONE change at a time, validate after each change
- Run validation suite after code changes: `cd AgentQMS/interface && make validate`
- Never skip validation steps
- Document any unexpected issues in Risk section
- Update Progress Tracker after every task

**Audit Reference**: `/workspaces/blog-creator-agent/docs/artifacts/assessments/2025-11-29_1642_assessment-artifact-naming-terminology-conflicts.md`

---

# Living Implementation Blueprint: Artifact Naming Convention Standardization

## Progress Tracker
- **STATUS:** Not Started - Awaiting Phase 1 Kickoff
- **CURRENT PHASE:** Phase 1 - Critical Foundation Fixes
- **CURRENT STEP:** Task 1.1 - Terminology Standardization in Validation Script
- **LAST COMPLETED TASK:** None
- **NEXT TASK:** Update variable names in `validate_artifacts.py` from "prefix" terminology to "artifact_type"

### Implementation Outline (Checklist)

#### **Phase 1: Critical Foundation Fixes (PRIORITY: CRITICAL)**

1. [ ] **Task 1.1: Terminology Standardization in Code**
   - [ ] Update `AgentQMS/agent_tools/compliance/validate_artifacts.py`:
     - [ ] Rename `_BUILTIN_PREFIXES` → `_BUILTIN_ARTIFACT_TYPES`
     - [ ] Rename `valid_prefixes` → `valid_artifact_types` (all occurrences)
     - [ ] Update variable names in methods
   - [ ] Update error messages to use "artifact type" not "prefix"
   - [ ] Run validation: `cd AgentQMS/interface && make validate`

2. [ ] **Task 1.2: Add Audit Artifact Type and Fix Directory Mappings**
   - [ ] Add `"audit-": "docs/artifacts/audits/"` to `_BUILTIN_ARTIFACT_TYPES`
   - [ ] Update ALL existing paths to use `docs/artifacts/` prefix:
     - [ ] `"implementation_plan_": "docs/artifacts/implementation_plans/"`
     - [ ] `"assessment-": "docs/artifacts/assessments/"`
     - [ ] `"design-": "docs/artifacts/design_documents/"`
     - [ ] `"research-": "docs/artifacts/research/"`
     - [ ] `"template-": "docs/artifacts/templates/"`
     - [ ] `"BUG_": "docs/artifacts/bug_reports/"`
     - [ ] `"SESSION_": "docs/artifacts/completed_plans/completion_summaries/session_notes/"`
   - [ ] Create directory: `mkdir -p docs/artifacts/audits`
   - [ ] Run validation: `cd AgentQMS/interface && make validate`

3. [ ] **Task 1.3: Add Root-Level Artifacts Directory Validation**
   - [ ] Add `validate_artifacts_root()` method to `ArtifactValidator` class
   - [ ] Implement logic to reject paths starting with `artifacts/` (without `docs/`)
   - [ ] Implement logic to enforce `docs/artifacts/` prefix
   - [ ] Call validation in `validate_single_file()` method
   - [ ] Test with files in both locations
   - [ ] Run validation: `cd AgentQMS/interface && make validate`

4. [ ] **Task 1.4: Fix Directory Validation Logic Bug**
   - [ ] Locate `validate_directory_placement()` method (Line ~278-297)
   - [ ] Replace `filename.startswith(prefix)` logic with regex extraction
   - [ ] Extract artifact_type from timestamp-first format: `^\d{4}-\d{2}-\d{2}_\d{4}_([^_-]+)`
   - [ ] Match extracted type against `valid_artifact_types` dictionary
   - [ ] Test with actual files
   - [ ] Run validation: `cd AgentQMS/interface && make validate`

5. [ ] **Task 1.5: Update Legacy Shim File**
   - [ ] Apply same changes to `AgentQMS/toolkit/compliance/validate_artifacts.py`
   - [ ] Ensure consistency between agent_tools and toolkit versions
   - [ ] Run validation: `cd AgentQMS/interface && make validate`

#### **Phase 2: Documentation Standardization (PRIORITY: HIGH)**

6. [ ] **Task 2.1: Update Single Source of Truth (system.md)**
   - [ ] Open `AgentQMS/knowledge/agent/system.md`
   - [ ] Replace all instances of `[prefix]` with `{ARTIFACT_TYPE}`
   - [ ] Update format specification to: `YYYY-MM-DD_HHMM_{ARTIFACT_TYPE}_description.md`
   - [ ] Add explicit table of valid artifact types
   - [ ] Add examples for each type
   - [ ] Remove ambiguous phrasing about "timestamp prefix"

7. [ ] **Task 2.2: Update Interface Documentation**
   - [ ] Update `AgentQMS/interface/README.md`
   - [ ] Replace "PREFIX"/"TYPE"/"document_type" with "ARTIFACT_TYPE"
   - [ ] Update all examples to show correct format
   - [ ] Add reference to system.md as SST

8. [ ] **Task 2.3: Update Tool Integration Docs**
   - [ ] Update `.qwen/README.md`
   - [ ] Replace `[TYPE]` with `{ARTIFACT_TYPE}`
   - [ ] Update format examples
   - [ ] Update validation command examples

9. [ ] **Task 2.4: Update Governance Documentation**
   - [ ] Update `AgentQMS/knowledge/protocols/governance/artifact_rules.md`
   - [ ] Standardize on "ARTIFACT_TYPE" terminology
   - [ ] Document root-level `/artifacts/` as forbidden
   - [ ] Add compliance checklist

10. [ ] **Task 2.5: Update CHANGELOG**
    - [ ] Add entry documenting terminology standardization
    - [ ] Document audit artifact type addition
    - [ ] Document directory structure enforcement
    - [ ] Reference audit report

#### **Phase 3: Validation and Testing (PRIORITY: HIGH)**

11. [ ] **Task 3.1: Comprehensive Validation Testing**
    - [ ] Run full validation suite: `cd AgentQMS/interface && make validate`
    - [ ] Verify all existing valid files still pass
    - [ ] Verify audit files validate correctly
    - [ ] Verify root-level artifacts are rejected
    - [ ] Verify error messages use new terminology

12. [ ] **Task 3.2: Compliance Check**
    - [ ] Run: `cd AgentQMS/interface && make compliance`
    - [ ] Address any boundary violations
    - [ ] Verify no regressions introduced

13. [ ] **Task 3.3: Error Message Verification**
    - [ ] Test with intentionally invalid files
    - [ ] Verify error messages are clear and use "artifact type"
    - [ ] Verify error messages guide to correct format
    - [ ] Verify root-level artifacts error message includes move instructions

14. [ ] **Task 3.4: Cross-Reference Testing**
    - [ ] Verify artifact creation workflow: `make create-assessment NAME=test TITLE="Test"`
    - [ ] Verify created files use correct format
    - [ ] Verify files placed in correct directories
    - [ ] Delete test artifacts after validation

---

## 📋 **Technical Requirements Checklist**

### **Code Changes**
- [ ] All variables renamed from "prefix" to "artifact_type" terminology
- [ ] Dictionary `_BUILTIN_PREFIXES` renamed to `_BUILTIN_ARTIFACT_TYPES`
- [ ] All paths prefixed with `docs/artifacts/` (never root `artifacts/`)
- [ ] `audit-` artifact type registered with directory `docs/artifacts/audits/`
- [ ] Root-level artifacts validation function implemented
- [ ] Directory validation bug fixed (extract from timestamp-first format)
- [ ] Both `agent_tools` and `toolkit` versions updated consistently

### **Documentation Changes**
- [ ] `system.md` uses `{ARTIFACT_TYPE}` consistently (SST)
- [ ] All README files updated with new terminology
- [ ] Governance docs updated
- [ ] CHANGELOG updated with standardization notes
- [ ] All examples use correct format: `YYYY-MM-DD_HHMM_{ARTIFACT_TYPE}_description.md`
- [ ] Table of valid artifact types added to docs

### **Validation Requirements**
- [ ] Validation suite passes with 100% existing valid files
- [ ] Audit artifacts validate correctly
- [ ] Root-level `/artifacts/` paths rejected with clear error
- [ ] Error messages use "artifact type" not "prefix"
- [ ] Directory placement validation works correctly
- [ ] Compliance check passes with no new violations

### **File System Changes**
- [ ] Directory created: `docs/artifacts/audits/`
- [ ] No files created in root-level `/artifacts/`
- [ ] All artifact types have correct directory mappings

---

## 🎯 **Success Criteria Validation**

### **Terminology Consistency (CRITICAL)**
- [ ] grep search for "valid_prefixes" returns 0 hits in `validate_artifacts.py`
- [ ] grep search for "valid_artifact_types" confirms all occurrences updated
- [ ] Error messages use "artifact type" not "file type prefix"
- [ ] Documentation uses `{ARTIFACT_TYPE}` not `[PREFIX]` or `[TYPE]`

### **Functional Validation (CRITICAL)**
- [ ] Validation suite: 77.2% → target 85%+ compliance (13 invalid files addressed)
- [ ] Audit artifacts validate successfully
- [ ] Root-level `/artifacts/` paths rejected with clear error message
- [ ] Directory placement validation works for timestamp-first format
- [ ] All 8 artifact types have correct `docs/artifacts/{type}/` mappings

### **AI Agent Success Metrics (from Audit)**
- [ ] Reduce failed bulk operations from 67% → <5% (test with batch validation)
- [ ] Zero infinite rename loops (test with format ambiguity scenarios)
- [ ] Zero cross-reference breakage (validate internal links)
- [ ] Error messages achieve >95% agent comprehension (test interpretation)

### **Code Quality**
- [ ] No syntax errors after changes
- [ ] Type hints maintained
- [ ] Docstrings updated where terminology changed
- [ ] No regressions in existing valid files
- [ ] Both agent_tools and toolkit versions consistent

---

## 📊 **Risk Mitigation & Fallbacks**

### **Current Risk Level**: MEDIUM
**Reason**: Changes affect core validation system used by all artifact operations

### **Identified Risks from Audit**:
1. **Breaking existing workflows** - Validation changes could reject previously valid files
2. **Terminology inconsistency** - Missing occurrences could leave confusion
3. **Directory placement errors** - Bug fix could cause unintended side effects
4. **Plugin compatibility** - Plugin-registered types may not follow new rules

### **Active Mitigation Strategies**:
1. **One change at a time**: Make single atomic changes, validate immediately
2. **Backup strategy**: Git commits after each successful task completion
3. **Testing before proceeding**: Run validation suite after every code change
4. **Audit reference**: Cross-check all changes against audit recommendations
5. **Legacy support maintained**: Don't remove old file detection, add warnings

### **Fallback Options**:
1. **If validation breaks badly**: Revert last change via git, diagnose issue, retry with fix
2. **If audit directory causes issues**: Start with warning-only mode, enforce in Phase 2
3. **If terminology change is incomplete**: Run comprehensive grep search, create follow-up task
4. **If directory bug fix fails**: Document specific failure, implement alternative extraction logic
5. **If plugins break**: Add plugin compatibility layer, update plugin schema in separate task

### **Rollback Plan**:
```bash
# If critical failure occurs:
git log --oneline -10  # Review recent commits
git revert <commit-hash>  # Revert problematic change
cd AgentQMS/interface && make validate  # Verify rollback successful
# Document issue in this blueprint's Risk section
# Create specific fix task
```

---

## 🔄 **Blueprint Update Protocol**

**Update Triggers:**
- Task completion (move to next task)
- Blocker encountered (document and propose solution)
- Technical discovery (update approach if needed)
- Quality gate failure (address issues before proceeding)

**Update Format:**
1. Update Progress Tracker (STATUS, CURRENT STEP, LAST COMPLETED TASK, NEXT TASK)
2. Mark completed items with [x]
3. Add any new discoveries or changes to approach
4. Update risk assessment if needed

---

## 🚀 **Immediate Next Action**

**TASK 1.1:** Update variable names in `validate_artifacts.py` from "prefix" terminology to "artifact_type"

**OBJECTIVE:** Establish consistent "artifact_type" terminology in core validation script, eliminating the "prefix" vs "type" vs "document_type" confusion

**FILE TO EDIT:** `/workspaces/blog-creator-agent/AgentQMS/agent_tools/compliance/validate_artifacts.py`

**APPROACH:**
1. **Rename class variable** (Line ~79-87):
   - `_BUILTIN_PREFIXES` → `_BUILTIN_ARTIFACT_TYPES`
   - Update dictionary keys remain same (the actual prefix strings like "assessment-")
   - Update dictionary values later in Task 1.2

2. **Rename instance variable** (Line ~130):
   - `self.valid_prefixes` → `self.valid_artifact_types`
   - Update all method parameters and variables

3. **Update error messages** (Line ~241-243, and elsewhere):
   - Change: `"Missing valid file type prefix. Valid prefixes: {valid_prefixes_str}"`
   - To: `"Missing valid artifact type. Valid artifact types: {valid_types_str}"`

4. **Update method implementations**:
   - `validate_naming_convention()`: Update variable names
   - `validate_directory_placement()`: Update variable names (prepare for bug fix in 1.4)
   - `_load_plugin_extensions()`: Update references to prefixes

5. **Run validation**:
   ```bash
   cd /workspaces/blog-creator-agent/AgentQMS/interface
   make validate
   ```

6. **Verify no syntax errors**:
   ```bash
   python -m py_compile /workspaces/blog-creator-agent/AgentQMS/agent_tools/compliance/validate_artifacts.py
   ```

7. **Git commit**:
   ```bash
   git add AgentQMS/agent_tools/compliance/validate_artifacts.py
   git commit -m "refactor: rename prefix terminology to artifact_type in validator"
   ```

**SUCCESS CRITERIA:**
- ✅ Zero occurrences of `valid_prefixes` variable name (grep confirms)
- ✅ All occurrences use `valid_artifact_types` instead
- ✅ Error messages use "artifact type" not "file type prefix"
- ✅ Validation suite runs without syntax errors
- ✅ Existing valid files still pass validation (no regressions)
- ✅ Git commit created with changes

**ON SUCCESS:** Update Progress Tracker, mark Task 1.1 complete, proceed to Task 1.2

**ON FAILURE:** Document error in Risk section, analyze issue, attempt fix or rollback

---

## 📝 **Detailed Task Specifications**

### **Task 1.1 - Variable Renaming Details**

**Changes Required (by line number):**
```python
# Line 79: Class variable
_BUILTIN_ARTIFACT_TYPES: Dict[str, str] = {  # Changed from _BUILTIN_PREFIXES
    "implementation_plan_": "implementation_plans/",
    "assessment-": "assessments/",
    # ... rest unchanged for now
}

# Line 130: Instance variable initialization
self.valid_artifact_types = dict(self._BUILTIN_ARTIFACT_TYPES)

# Line 156-203: Plugin extension method
if "prefixes" in validators:  # Plugin schema still uses "prefixes" - OK for now
    self.valid_artifact_types.update(validators["prefixes"])

# Line 228-238: Validation method
has_valid_artifact_type = any(
    after_timestamp.startswith(artifact_type) for artifact_type in self.valid_artifact_types
)
if not has_valid_artifact_type:
    valid_types_str = ", ".join(self.valid_artifact_types.keys())
    return (
        False,
        f"Missing valid artifact type. Valid artifact types: {valid_types_str}",
    )

# Line 278-297: Directory placement (will be fixed in 1.4, but update vars now)
for artifact_type, directory in self.valid_artifact_types.items():
    if filename.startswith(artifact_type):  # BUG remains, fix in Task 1.4
        expected_dir = directory.rstrip("/")
        break
```

**Grep Commands to Verify:**
```bash
# Should return 0 results after changes:
grep -n "valid_prefixes" /workspaces/blog-creator-agent/AgentQMS/agent_tools/compliance/validate_artifacts.py

# Should return multiple results after changes:
grep -n "valid_artifact_types" /workspaces/blog-creator-agent/AgentQMS/agent_tools/compliance/validate_artifacts.py

# Should return 0 results for old error message:
grep -n "file type prefix" /workspaces/blog-creator-agent/AgentQMS/agent_tools/compliance/validate_artifacts.py
```

---

*This implementation plan follows the Blueprint Protocol Template (PROTO-GOV-003) for systematic, autonomous execution with clear progress tracking.*