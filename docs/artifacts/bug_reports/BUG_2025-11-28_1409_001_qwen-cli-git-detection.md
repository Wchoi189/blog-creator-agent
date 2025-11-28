---
type: "bug_report"
category: "troubleshooting"
status: "active"
version: "1.0"
tags: ['bug', 'issue', 'troubleshooting', 'qwen-cli', 'git-detection']
title: "Qwen Coder CLI Fails to Detect Git on Linux Due to Shell Builtin Issue"
date: "2025-11-28 14:09 (KST)"
---

# Bug Report: Qwen Coder CLI Fails to Detect Git on Linux Due to Shell Builtin Issue

## Bug ID
BUG-001

## Summary
Qwen Coder CLI fails to detect Git installation on Linux systems, incorrectly reporting "Git is not installed" and disabling checkpointing functionality, even when Git is properly installed and accessible.

## Environment
- **OS**: Linux (Ubuntu/Debian-based distributions)
- **Node.js Version**: 20.19.6 (or compatible versions)
- **Qwen CLI Version**: 0.2.3
- **Git Version**: 2.34.1 (or any installed version)
- **Installation Method**: NPM global install (`npm install -g @qwen-code/qwen-code`)

## Steps to Reproduce
1. Install Git on Linux system: `sudo apt update && sudo apt install git`
2. Verify Git works: `git --version` returns version info
3. Install Qwen CLI globally: `npm install -g @qwen-code/qwen-code@latest`
4. Attempt to use checkpointing: `qwen -c -p "hello world"`

## Expected Behavior
Qwen CLI should detect Git installation and enable checkpointing functionality without errors.

## Actual Behavior
CLI throws error: "Checkpointing is enabled, but Git is not installed. Please install Git or disable checkpointing to continue."

## Error Messages
```
Command command not found
An unexpected critical error occurred:
Error: Checkpointing is enabled, but Git is not installed. Please install Git or disable checkpointing to continue.
    at GitService.initialize (file:///workspaces/.npm-global/lib/node_modules/@qwen-code/qwen-code/cli.js:218525:17)
    at Config.getGitService (file:///workspaces/.npm-global/lib/node_modules/@qwen-code/qwen-code/cli.js:245175:33)
    at Config.initialize (file:///workspaces/.npm-global/lib/node_modules/@qwen-code/qwen-code/cli.js:244790:22)
    at main (file:///workspaces/.npm-global/lib/node_modules/@qwen-code/qwen-code/cli.js:356010:18)
    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)
```

## Root Cause Analysis
The bug is in the `resolveCommandPath` function in `packages/core/src/utils/shell-utils.ts`. On Linux, the code attempts to check Git availability using:

```typescript
execFileSync('command', ['-v', 'git'], { encoding: 'utf8', shell: false })
```

However, `command` is a bash shell builtin, not an external executable. `execFileSync` cannot execute shell builtins without a shell, causing the check to fail and report Git as unavailable.

## Impact
- **Severity**: High - Core functionality (checkpointing) is broken on Linux
- **Affected Users**: All Linux users of Qwen CLI attempting to use checkpointing
- **Workaround**: Disable checkpointing with `-c` flag, or apply the code fix below

## Investigation
- Git is correctly installed and in PATH
- Manual execution of `command -v git` works in shell
- Node.js can execute Git directly via `execSync`
- Issue is specific to Qwen's Git detection logic

## Fix Applied
Modified `packages/core/src/utils/shell-utils.ts` line ~527:

**Before:**
```typescript
result = execFileSync(checkCommand, checkArgs, {
  encoding: 'utf8',
  shell: isWin,
}).trim();
```

**After:**
```typescript
result = execFileSync(checkCommand, checkArgs, {
  encoding: 'utf8',
  shell: true,
}).trim();
```

This allows shell builtins to work on Linux while maintaining Windows compatibility.

## Validation
- Built and tested fixed version (0.3.0)
- Checkpointing now works on Linux
- Git-dependent features functional
- No regression on Windows (theoretical, based on code change)

## References
- Qwen Code Repository: https://github.com/QwenLM/qwen-code
- Affected File: `packages/core/src/utils/shell-utils.ts`
- Issue affects versions 0.2.3 and earlier on Linux

## Notes
This bug report serves as reference for future Qwen CLI installations on Linux or Windows systems. The fix has been applied locally and validated.

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
High/Medium/Low

---

*This bug report follows the project's standardized format for issue tracking.*