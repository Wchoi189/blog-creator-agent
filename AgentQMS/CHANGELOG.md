# AgentQMS Framework Bug Fixes - AI Implementation Guide

## Qwen CLI Integration Bugs

### Bug: Checkpointing Git Detection Failure
**File**: `.qwen/settings.json`
**Issue**: Qwen CLI failed with "Checkpointing is enabled, but Git is not installed"
**Fix**: Set `"general": {"checkpointing": {"enabled": false}}`
**Implementation**: Add checkpointing disabled setting to prevent Git dependency issues

### Bug: Approval Mode Syntax Error
**File**: `.qwen/run.sh`
**Issue**: `--yolo` flag conflicted with `--approval-mode yolo`
**Fix**: Use `--approval-mode yolo` consistently in all scripts
**Implementation**: Update Qwen command syntax to use correct approval mode flags

### Bug: Memory Leak - Abort Signal Listeners
**File**: Qwen CLI operations
**Issue**: MaxListenersExceededWarning (11 abort listeners > 10 max)
**Fix**: Avoid running multiple simultaneous Qwen processes
**Implementation**: Add process management to prevent concurrent Qwen instances

## Validation System Bugs

### Bug: Incorrect Naming Regex Pattern
**File**: `.qwen/manual_validate.sh`
**Issue**: Regex expected `[TYPE]` uppercase instead of `[PREFIX]` format
**Fix**: Changed from `^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}_[A-Z]+_.+\.md$` to `^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}_(.+)\.md$`
**Implementation**: Update validation regex to match AgentQMS prefix-based naming

### Bug: Artifacts Path Configuration Mismatch
**File**: `.agentqms/settings.yaml`
**Issue**: Path pointed to wrong artifacts directory
**Fix**: Set `paths.artifacts: docs/artifacts`
**Implementation**: Ensure artifacts path matches actual directory structure

### Bug: Missing Frontmatter Opening Marker
**File**: Artifact files
**Issue**: Frontmatter fields present but missing opening `---`
**Fix**: Add `---` at start of YAML frontmatter
**Implementation**: Ensure all frontmatter starts with `---` marker

## Documentation Structure Bugs

### Bug: Loose Docs in Project Root
**File**: Project root directory
**Issue**: DOCS_INDEX.md, HANDOVER.md violated "no loose docs" rule
**Fix**: Move to `docs/` and `docs/artifacts/` respectively
**Implementation**: Enforce root directory policy (only README.md, CHANGELOG.md allowed)

### Bug: Inconsistent Artifact Naming
**File**: Artifact files
**Issue**: Files used various naming patterns instead of timestamped format
**Fix**: Rename to `YYYY-MM-DD_HHMM_[PREFIX]descriptive-name.md`
**Implementation**: Standardize naming convention across all artifacts

### Bug: Wrong Directory Structure
**File**: Artifact organization
**Issue**: Artifacts not organized by type in subdirectories
**Fix**: Create `docs/artifacts/{assessments,bug_reports,plans,etc}/` structure
**Implementation**: Implement type-based directory organization

## Configuration Bugs

### Bug: Inconsistent Path References
**Files**: Multiple config files
**Issue**: Scripts and configs referenced different artifact paths
**Fix**: Standardize all references to `docs/artifacts/`
**Implementation**: Audit and update all path references for consistency

### Bug: Missing Workspace Exclusions
**File**: `.qwen/settings.json`
**Issue**: Framework files could be accidentally modified
**Fix**: Add exclude patterns for `AgentQMS/`, `.agentqms/`, etc.
**Implementation**: Add comprehensive workspace exclusion patterns

### Bug: Incorrect Tool Permissions
**File**: `.qwen/settings.json`
**Issue**: Tools had insufficient permissions for autonomous operation
**Fix**: Set approval mode to "auto-edit" and add allowed tools list
**Implementation**: Configure appropriate tool permissions for AI operations

## Script Implementation Bugs

### Bug: Run Script Command Syntax
**File**: `.qwen/run.sh`
**Issue**: Qwen commands used incorrect flag syntax
**Fix**: Replace `--yolo` with `--approval-mode yolo`
**Implementation**: Update all Qwen command invocations with correct syntax

### Bug: Validation Script Path Hardcoding
**File**: `.qwen/manual_validate.sh`
**Issue**: Script hardcoded wrong artifacts directory path
**Fix**: Update `ARTIFACTS_DIR` variable to correct path
**Implementation**: Make artifact paths configurable or dynamically resolved

### Bug: Frontmatter Generation Missing Opening Marker
**File**: Artifact creation scripts
**Issue**: Generated frontmatter missing opening `---`
**Fix**: Ensure YAML frontmatter always starts with `---`
**Implementation**: Update frontmatter generation templates