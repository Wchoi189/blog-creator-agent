# Audits

Framework audits, compliance checks, and quality evaluations with automated implementation plan generation.

## Purpose

This directory contains comprehensive audits of the codebase, framework, and processes. Audits identify issues, evaluate compliance with standards, and recommend improvements.

## GitHub Actions Automation

When an audit file's status is changed to `completed` and pushed to the main branch:

1. **GitHub Actions workflow triggers** (`.github/workflows/audit-completion.yml`)
2. **Extracts audit findings** from the completed audit
3. **Generates implementation plan template** as draft PR
4. **Creates Pull Request** with:
   - Auto-generated plan template
   - Audit findings summary
   - Approval checklist
   - Instructions to complete with GitHub Copilot

## Cross-Linking Conventions

Use relative paths for artifact references:

- **Related implementation plans**: `../implementation_plans/YYYY-MM-DD_HHMM_implementation_plan_name.md`
- **Related audits**: `./YYYY-MM-DD_HHMM_audit-name.md`
- **Source documents**: `../path/to/document.md`

### Frontmatter Fields

```yaml
related_artifacts: []      # Links to source documents
generated_artifacts: []    # Links to plans created from this audit
```

Update `generated_artifacts` manually after PR merge to maintain bidirectional tracking.

## Audit Categories

- **accessibility** - WCAG compliance, screen reader support, keyboard navigation
- **security** - Security vulnerabilities, authentication, authorization
- **compliance** - Framework compliance, naming conventions, structure
- **performance** - Performance bottlenecks, optimization opportunities
- **code_quality** - Code style, best practices, maintainability
- **framework** - AgentQMS framework adherence, protocol compliance

## Naming Convention

Format: `YYYY-MM-DD_HHMM_audit-{descriptive-name}.md`

Examples:
- `2025-11-29_1200_audit-accessibility.md`
- `2025-11-29_1500_audit-security-review.md`
- `2025-11-29_1800_audit-framework-compliance.md`

## Required Sections

All audit files must include:

1. **Executive Summary** - High-level overview and compliance status
2. **Findings** - Detailed issues with severity levels (🔴 Critical, 🟡 High, 🟢 Medium)
3. **Recommendations** - Prioritized action items with timelines
4. **Compliance Status** - Overall compliance assessment and scores
5. **Related Artifacts** - Cross-references to related documents and generated plans

## Status Values

- `draft` - Audit in progress
- `active` - Audit underway
- `completed` - Audit finished (triggers automation)
- `archived` - Historical audit

## Local Development Workflow

When working locally without pushing to GitHub:

1. Create audit: `make create-audit NAME=my-audit TITLE="My Audit"`
2. Complete audit sections and set `status: completed`
3. Manually create implementation plan:
   ```bash
   make create-plan NAME=fix-my-audit TITLE="Address My Audit Findings"
   ```
4. Update audit's `generated_artifacts` field with relative path to plan

## Files

### Accessibility Audits

- [Accessibility (a11y) Audit](2025-11-29_1200_audit-accessibility.md) - WCAG 2.1 AA compliance audit with 8 critical issues

### Security Audits

_None yet_

### Compliance Audits

_None yet_

### Performance Audits

_None yet_

### Code Quality Audits

_None yet_

### Framework Audits

_None yet_

---

**Total Audits**: 1  
**Last Updated**: 2025-11-29
