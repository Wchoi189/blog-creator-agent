# AgentQMS Automation Scripts Fix Plan

## Executive Summary

This document outlines the comprehensive plan to fix critical issues in the AgentQMS framework's automation scripts and documentation. The issues were identified through analysis of another project's AgentQMS implementation and involve inconsistencies between documentation, error messages, and actual implementation.

## Issues Identified

### Issue 1: Documentation References Incorrectly Use `[TYPE]` Instead of `[PREFIX]`

**Problem**: The framework documentation and error messages incorrectly reference `[TYPE]` in naming patterns, when the actual implementation uses prefixes.

**Impact**: Users receive confusing error messages that don't match the actual naming conventions used by the framework.

**Evidence**: From another project's analysis, the framework uses prefixes like:
- `implementation_plan_` (not `IMPLEMENTATION_PLAN_`)
- `assessment-`
- `design-`
- `research-`
- `template-`
- `BUG_`
- `SESSION_`

### Issue 2: Incorrect Prefix Mappings in Automation Scripts

**Problem**: The automation scripts contain incorrect prefix mappings that cause wrong type detection and prefix assignment.

**Specific Issues**:
- `fix_naming_conventions.py` uses `"IMPLEMENTATION_PLAN_"` instead of `"implementation_plan_"`
- `reorganize_files.py` has inconsistent prefix mappings
- Scripts assign wrong prefixes to files based on incorrect type detection

**Impact**: Automated compliance fixes produce incorrect results, potentially breaking file organization and naming conventions.

## Required Fixes

### Fix Set 1: Update Documentation References (4 files)

#### 1.1 `AgentQMS/agent_tools/compliance/validate_artifacts.py` (line ~592)
```python
# BEFORE
suggestions.append(
    "      Format: YYYY-MM-DD_HHMM_[TYPE]_descriptive-name.md"
)

# AFTER
suggestions.append(
    "      Format: YYYY-MM-DD_HHMM_[PREFIX]_descriptive-name.md"
)
```

#### 1.2 `AgentQMS/toolkit/compliance/validate_artifacts.py` (line ~491)
```python
# BEFORE
suggestions.append(
    "      Format: YYYY-MM-DD_HHMM_[TYPE]_descriptive-name.md"
)

# AFTER
suggestions.append(
    "      Format: YYYY-MM-DD_HHMM_[PREFIX]_descriptive-name.md"
)
```

#### 1.3 `AgentQMS/knowledge/protocols/governance/artifact_rules.md` (line ~17)
```markdown
<!-- BEFORE -->
- **File naming**: Always use `YYYY-MM-DD_HHMM_[TYPE]_descriptive-name.md`.

<!-- AFTER -->
- **File naming**: Always use `YYYY-MM-DD_HHMM_[PREFIX]_descriptive-name.md`.
```

#### 1.4 `AgentQMS/knowledge/agent/system.md` (line ~55)
```markdown
<!-- BEFORE -->
- Required frontmatter and naming: `YYYY-MM-DD_HHMM_[type]_descriptive-name.md`.

<!-- AFTER -->
- Required frontmatter and naming: `YYYY-MM-DD_HHMM_[prefix]_descriptive-name.md`.
```

### Fix Set 2: Correct Prefix Mappings in Automation Scripts (3 locations)

#### 2.1 `AgentQMS/toolkit/maintenance/fix_naming_conventions.py` (line ~321)
```python
# BEFORE
type_to_prefix = {
    "implementation_plan": "IMPLEMENTATION_PLAN_",
    "assessment": "assessment-",
    # ... other mappings
}

# AFTER
type_to_prefix = {
    "implementation_plan": "implementation_plan_",
    "assessment": "assessment-",
    # ... other mappings
}
```

#### 2.2 `AgentQMS/toolkit/maintenance/reorganize_files.py` (line ~42)
```python
# BEFORE
self.valid_prefixes = {
    "IMPLEMENTATION_PLAN_": "implementation_plans/",
    "assessment-": "assessments/",
    # ... other mappings
}

# AFTER
self.valid_prefixes = {
    "implementation_plan_": "implementation_plans/",
    "assessment-": "assessments/",
    # ... other mappings
}
```

#### 2.3 `AgentQMS/toolkit/maintenance/reorganize_files.py` (line ~52)
```python
# BEFORE
"implementation_plans": {
    "description": "Implementation plans and blueprints",
    "prefixes": ["IMPLEMENTATION_PLAN_"],
    "types": ["implementation_plan"],
},

# AFTER
"implementation_plans": {
    "description": "Implementation plans and blueprints",
    "prefixes": ["implementation_plan_"],
    "types": ["implementation_plan"],
},
```

## Implementation Plan

### Phase 1: Documentation Fixes
**Duration**: 15 minutes
**Risk Level**: Low
**Steps**:
1. Apply sed commands to replace `[TYPE]` with `[PREFIX]` in 4 files
2. Verify changes don't break other references
3. Commit documentation fixes

### Phase 2: Automation Script Fixes
**Duration**: 20 minutes
**Risk Level**: Medium
**Steps**:
1. Update prefix mappings in 3 locations
2. Verify syntax correctness
3. Test dry-run functionality
4. Commit automation script fixes

### Phase 3: Validation and Testing
**Duration**: 30 minutes
**Risk Level**: Low
**Steps**:
1. Run `cd AgentQMS/interface && make validate`
2. Test dry-run mode on fixed scripts
3. Verify compliance checking works correctly
4. Run full compliance check

### Phase 4: Production Testing
**Duration**: 45 minutes
**Risk Level**: High
**Steps**:
1. Create backup branch
2. Run automated compliance fixes on test files
3. Verify results are correct
4. Roll back if issues found

## Success Criteria

### Functional Criteria
- [ ] All documentation references use `[PREFIX]` instead of `[TYPE]`
- [ ] Automation scripts use correct prefix mappings
- [ ] Dry-run tests show correct prefix assignment
- [ ] Framework validation passes without errors
- [ ] Compliance checking works properly

### Quality Criteria
- [ ] No syntax errors introduced
- [ ] No breaking changes to existing functionality
- [ ] Error messages are clear and accurate
- [ ] Documentation matches implementation

### Performance Criteria
- [ ] Automated fixes complete within reasonable time
- [ ] No performance degradation in validation scripts
- [ ] Memory usage remains acceptable

## Risk Assessment

### Low Risk Items
- Documentation string replacements
- Prefix mapping corrections
- Framework validation runs

### Medium Risk Items
- Automation script logic changes
- Type detection algorithm modifications

### High Risk Items
- Running automated fixes on production files
- Potential for incorrect file moves/renames

## Mitigation Strategies

### For Documentation Fixes
- Use sed with preview mode first
- Manual verification of changes
- Git diff review before commit

### For Automation Script Fixes
- Test on isolated files first
- Dry-run mode validation
- Backup creation before any file operations

### For Production Testing
- Create feature branch for testing
- Test on subset of files first
- Have rollback plan ready

## Dependencies

### Tools Required
- sed or similar text processing tool
- Git for version control
- Python 3.8+ for testing
- Make for framework validation

### Knowledge Required
- AgentQMS framework structure
- Python scripting
- Bash/shell commands
- Git version control

## Timeline

| Phase | Duration | Start Date | End Date | Status |
|-------|----------|------------|----------|--------|
| Documentation Fixes | 15 min | TBD | TBD | Pending |
| Automation Script Fixes | 20 min | TBD | TBD | Pending |
| Validation and Testing | 30 min | TBD | TBD | Pending |
| Production Testing | 45 min | TBD | TBD | Pending |

## Rollback Plan

1. **Immediate Rollback**: `git reset --hard HEAD~1` for last commit
2. **Selective Rollback**: `git revert <commit-hash>` for specific changes
3. **File-level Recovery**: Restore from backups created during testing
4. **Full Repository Reset**: `git reset --hard <backup-branch>` if needed

## Communication Plan

- **Internal**: Document all changes in commit messages
- **Testing**: Log test results and any issues found
- **Completion**: Update this document with actual results
- **Issues**: Document any problems encountered and resolutions

## Post-Implementation

### Monitoring
- Monitor automated compliance fix results
- Check for any new validation errors
- Verify user feedback on error messages

### Follow-up Tasks
- Update any related documentation
- Consider adding automated tests for prefix mappings
- Review other AgentQMS projects for similar issues

### Lessons Learned
- Document what worked well and what didn't
- Update this plan template for future fixes
- Consider adding validation for prefix consistency

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-28 | 1.0 | Initial plan creation |

## Approval

| Role | Name | Date | Status |
|------|------|------|--------|
| Author | AI Assistant | 2025-11-28 | Approved |
| Reviewer | TBD | TBD | Pending |
| Approver | TBD | TBD | Pending |</content>
<parameter name="filePath">/workspaces/blog-creator-agent/AGENTQMS_FIX_PLAN.md