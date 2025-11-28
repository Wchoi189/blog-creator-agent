---
type: "implementation_plan"
category: "development"
status: "active"
version: "1.0"
tags: ['implementation', 'plan', 'development']
title: "Fix Critical Bugs in Automated Compliance Fix Script"
date: "2025-11-28 22:07 (KST)"
---

# Master Prompt

You are an autonomous AI agent, my Chief of Staff for implementing the **Fix Critical Bugs in Automated Compliance Fix Script**. Your primary responsibility is to execute the "Living Implementation Blueprint" systematically, handle outcomes, and keep track of our progress. Do not ask for clarification on what to do next; your next task is always explicitly defined.

---

## Problem Statement

The automated compliance fix script (`AgentQMS/toolkit/automated_compliance_fix.sh`) has critical bugs causing data corruption:

### Critical Issues Identified:
1. **No Processing Limits**: Processes all files despite user specifying "fix 3 files max"
2. **Flawed Content Analysis**: Misclassifies documents (implementation plans → assessments)
3. **Incorrect Naming**: Applies wrong prefixes (`implementation_plan_` instead of `assessment-`)
4. **Wrong Relocations**: Moves files to incorrect directories based on low-confidence content analysis
5. **No Validation Gates**: No pre-execution validation or safety checks
6. **No Rollback**: Cannot undo failed operations automatically

### Impact:
- **Severity**: HIGH (data corruption)
- **Affected Files**: 52+ files incorrectly modified in last run
- **Recovery**: Manual git reset required

### Root Causes:
- `automated_compliance_fix.sh`: No limit parameter implementation
- `reorganize_files.py`: Content analysis uses simplistic keyword matching with unreliable confidence scores
- `fix_naming_conventions.py`: Wrong prefix-to-directory mappings
- All scripts: No dry-run mode, no validation gates, no rollback mechanism

### Detailed Analysis:

#### File: `automated_compliance_fix.sh`
**Issues:**
- No command-line parsing for `--max-files` parameter
- Calls Python scripts without passing any limit
- No tracking of total files processed across all operations
- Runs all 5 fix operations sequentially without limit checking

**Required Changes:**
- Add getopts parsing for `--max-files` and `--dry-run`
- Track cumulative file count across operations
- Exit early when limit reached
- Pass limit to each Python script

#### File: `reorganize_files.py`
**Issues:**
- Lines 180-250: Content analysis uses basic regex patterns with no context
- Lines 234-240: `_determine_directory_from_content()` returns first pattern match
- Lines 305-330: Duplicate filename handling adds `_1` suffix (data corruption)
- No confidence threshold enforcement (accepts any >0.0 score)

**Required Changes:**
- Prioritize frontmatter `type` field (lines 226-232)
- Add minimum confidence threshold of 0.85
- Remove duplicate filename `_1` suffix logic
- Add validation before executing moves

#### File: `fix_naming_conventions.py`
**Issues:**
- Lines 45-55: Prefix mapping has wrong values (e.g., `IMPLEMENTATION_PLAN_` vs `implementation_plan_`)
- Lines 170-195: Content type detection returns first match without validation
- Lines 240-270: No validation that inferred type matches current directory
- Applies multiple operations to same file sequentially without conflict checking

**Required Changes:**
- Fix prefix mappings to match actual conventions
- Validate type inference against directory context
- Check for conflicts before applying multiple operations
- Add limit parameter and counter

---

**Your Core Workflow is a Goal-Execute-Update Loop:**
1. **Goal:** A clear `🎯 Goal` will be provided for you to achieve.
2. **Execute:** You will start working on the task defined in the `NEXT TASK`
3. **Handle Outcome & Update:** Based on the success or failure of the command, you will follow the specified contingency plan. Your response must be in two parts:
   * **Part 1: Execution Report:** Provide a concise summary of the results and analysis of the outcome (e.g., "All tests passed" or "Test X failed due to an IndexError...").
   * **Part 2: Blueprint Update Confirmation:** Confirm that the living blueprint has been updated with the new progress status and next task. The updated blueprint is available in the workspace file.

---

# Living Implementation Blueprint: Fix Critical Bugs in Automated Compliance Fix Script

## Progress Tracker
- **STATUS:** In Progress - Phase 1 Complete, Phase 2 Partial
- **CURRENT STEP:** Phase 2, Task 2.1 - Improve File Type Detection
- **LAST COMPLETED TASK:** Phase 1 complete - Added processing limits and dry-run mode
- **NEXT TASK:** Fine-tune content analysis to avoid misclassifications

### Implementation Outline (Checklist)

#### **Phase 1: Add Processing Controls (Day 1-2)** ✅ COMPLETE
1. [x] **Task 1.1: Add Processing Limits**
   - [x] Add `--max-files` parameter to `automated_compliance_fix.sh`
   - [x] Add `--limit` parameter to all Python fix scripts
   - [x] Implement early exit when limit reached in each script
   - [x] Add progress counter and limit tracking

2. [x] **Task 1.2: Implement Dry-Run Mode**
   - [x] Add `--dry-run` flag to main bash script
   - [x] Ensure all Python scripts respect dry-run mode (fix_naming_conventions.py and reorganize_files.py)
   - [x] Display detailed change preview without modifications
   - [ ] Add confirmation prompt before actual execution (deferred - dry-run provides preview)

#### **Phase 2: Fix Content Analysis Logic (Day 3-4)** ⚠️ PARTIAL
3. [x] **Task 2.1: Improve File Type Detection**
   - [x] Fix `reorganize_files.py` content analysis patterns (improved with match counting)
   - [x] Prioritize frontmatter `type` field over content analysis (returns 0.95 confidence)
   - [x] Add confidence threshold for content-based moves (0.85 minimum)
   - [x] Prevent moves below 0.85 confidence score
   - [ ] ⚠️ Need to prevent misclassification of index/registry files

4. [x] **Task 2.2: Fix Naming Convention Rules**
   - [x] Fix `fix_naming_conventions.py` prefix mapping (`implementation_plan_` not `IMPLEMENTATION_PLAN_`)
   - [x] Validate prefix matches expected directory
   - [ ] Add type validation before applying prefix (needs more work)
   - [ ] Fix timestamp format validation (needs review)

#### **Phase 3: Add Safety & Validation (Day 5-6)**
5. [ ] **Task 3.1: Pre-execution Validation**
   - [ ] Validate all proposed changes before execution
   - [ ] Check for duplicate filenames
   - [ ] Verify target directories exist
   - [ ] Detect circular moves or conflicts

6. [ ] **Task 3.2: Rollback Mechanism**
   - [ ] Store operation manifest before execution
   - [ ] Implement automated rollback function
   - [ ] Add rollback command to bash script
   - [ ] Test rollback with various failure scenarios

#### **Phase 4: Testing & Documentation (Day 7)**
7. [ ] **Task 4.1: Comprehensive Testing**
   - [ ] Test with 1-3 file limits
   - [ ] Test dry-run mode accuracy
   - [ ] Test rollback functionality
   - [ ] Test with various file types and violations

8. [ ] **Task 4.2: Update Documentation**
   - [ ] Update script usage documentation
   - [ ] Add examples for common scenarios
   - [ ] Document safety features and limitations
   - [ ] Update bug report with resolution

---

## 📋 **Technical Requirements Checklist**

### **Architecture & Design**
- [ ] Maintain separation between bash orchestration and Python execution
- [ ] Keep existing backup mechanism and extend it
- [ ] Use consistent parameter naming across all scripts
- [ ] Add operation manifest for rollback capability

### **Integration Points**
- [ ] Maintain compatibility with existing AgentQMS validation tools
- [ ] Preserve current directory structure and naming conventions
- [ ] Work with existing frontmatter format and metadata
- [ ] Integrate with git for change tracking

### **Quality Assurance**
- [ ] Test with edge cases (1 file, 100+ files, mixed violations)
- [ ] Validate no data corruption occurs
- [ ] Ensure dry-run matches actual execution
- [ ] Test rollback recovers original state completely

---

## 🎯 **Success Criteria Validation**

### **Functional Requirements**
- [ ] Script respects user-specified file limits (e.g., "fix 3 files max")
- [ ] Content analysis correctly identifies document types with >85% confidence
- [ ] Naming conventions applied match established rules
- [ ] Files moved to correct directories based on type
- [ ] Dry-run mode accurately previews all changes
- [ ] Rollback successfully restores original state

### **Technical Requirements**
- [ ] No data corruption or loss occurs
- [ ] No duplicate files with "_1" suffixes created
- [ ] All scripts have proper error handling
- [ ] Command-line parameters properly validated
- [ ] Backup mechanism preserves all original data
- [ ] Operation manifest tracks all changes for rollback

---

## 📊 **Risk Mitigation & Fallbacks**

### **Current Risk Level**: HIGH (Data corruption risk)
### **Active Mitigation Strategies**:
1. **Always create backups** before any modifications
2. **Mandatory dry-run** before actual execution
3. **Implement rollback** for all operations
4. **Test incrementally** with small file sets first
5. **Add validation gates** before each modification

### **Fallback Options**:
1. **If content analysis fails**: Use only frontmatter type field, skip content-based detection
2. **If automated rollback fails**: Provide manual git reset instructions with commit hash
3. **If confidence thresholds too restrictive**: Allow manual override with explicit confirmation
4. **If bulk operations fail**: Switch to single-file mode with user confirmation each step

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

**TASK:** Add Processing Limits to Automated Compliance Fix Script

**OBJECTIVE:** Implement `--max-files` parameter in bash script and `--limit` parameter in all Python fix modules to respect user-specified processing constraints

**APPROACH:**
1. Add `--max-files N` parameter to `automated_compliance_fix.sh`
2. Pass limit parameter to each Python script invocation
3. Implement counter and early exit in `fix_naming_conventions.py`
4. Implement counter and early exit in `reorganize_files.py`
5. Add progress reporting showing "X of N files processed"

**SUCCESS CRITERIA:**
- Running `./automated_compliance_fix.sh --max-files 3` processes exactly 3 files
- Script exits early when limit reached
- Progress counter accurately reflects files processed
- All Python modules respect the limit parameter

---

*This implementation plan follows the Blueprint Protocol Template (PROTO-GOV-003) for systematic, autonomous execution with clear progress tracking.*