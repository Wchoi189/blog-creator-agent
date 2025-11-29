---
title: "Cloud-Autonomous AgentQMS Artifact Workflow Remediation Plan"
date: "2025-11-29 18:22 (KST)"
type: "implementation_plan"
category: "planning"
status: "active"
version: "1.0"
tags: ["AgentQMS", "automation", "CI", "validation", "autofix", "planning"]
---

# Cloud-Autonomous AgentQMS Artifact Workflow Remediation Plan

Reference assessment: ../assessments/2025-11-29_1810_assessment-agentqms-artifact-workflow-review.md

## Objective
Design and implement a cloud-executed, autonomous workflow that raises overall documentation compliance from structural-only checks to end-to-end integrity (naming, placement, cross-validation, link health), while providing a safe auto-fix path with preview and limits.

## Scope
- In-scope: Validator enhancements, link checks, automated index (re)generation, safe auto-fix tool, CI workflows, developer ergonomics.
- Out-of-scope: Content rewriting, editorial quality, or semantic correctness of artifacts.

## Non-Goals
- No changes to artifact content aside from link/path updates necessary for integrity.
- No breaking changes to existing directory taxonomy without prior RFC.

## Guiding Principles
- Safety first: dry-run by default, explicit `--commit` option.
- Deterministic outputs: stable ordering, idempotent runs.
- Human-in-the-loop: clear diffs, small-scoped batches (e.g., `--limit 10`).

## Architecture Overview
- Validator core: extend `AgentQMS/agent_tools/compliance/validate_artifacts.py` with structured JSON output mode.
- Auto-fix CLI: new tool under `AgentQMS/agent_tools/utilities/autofix_artifacts.py` consuming validator JSON.
- Index builder: `AgentQMS/agent_tools/documentation/reindex_artifacts.py` to rebuild indexes.
- Link checker: `AgentQMS/agent_tools/documentation/check_links.py` to verify Markdown links to artifacts.
- Make targets: wire `validate`, `reindex`, `check-links`, `fix` via `AgentQMS/interface/Makefile`.
- CI (cloud autonomy): GitHub Actions workflow (`.github/workflows/agentqms-ci.yml`) to run validate, reindex, link check on PR; optional branch workflow to run safe autofix (`--limit 10`) and open PR.

## Work Packages

### Phase 1 — Rules & Messages (High)
Deliverables:
- Unified naming schema (machine-readable YAML/JSON) mapping artifact types → prefix/separator/case/dir.
- Improved messages: differentiate “missing type” vs “invalid format for type”.
Actions:
- Add `AgentQMS/knowledge/agent/artifact_rules.yaml` and load in validator.
- Update diagnostics to include expected pattern beside each violation.

### Phase 2 — Cross-Validation & Placement (High)
Deliverables:
- Frontmatter ↔ filename ↔ directory consistency checks.
- Single consolidated diagnostic when multiple mismatches occur.
Actions:
- Parse frontmatter (`type:`) and compare against schema + filename prefix + directory.
- Add rule to flag mismatched combinations with suggested relocation and rename.

### Phase 3 — Link Integrity + Index Regeneration (High)
Deliverables:
- `make reindex`: regenerate all artifact indexes deterministically.
- `make check-links`: verify index links and inline Markdown links to artifacts.
Actions:
- Implement index builder scanning `docs/artifacts/**` by type.
- Implement link checker using Markdown parser and filesystem lookups.

### Phase 4 — Safe Auto-Fix Pipeline (Medium)
Deliverables:
- `validate --json` output for programmatic consumption.
- `make fix ARGS="--limit N --dry-run --commit --update-links"` applying `git mv` and rewriting affected links + reindex.
Actions:
- Build `autofix_artifacts.py` that reads validator JSON and performs ordered operations: rename/move → link rewrite → reindex → re-validate.
- Handle duplicate destinations (e.g., `bug_report_*` vs `BUG_*`) with conflict policy: prefer canonical target, delete or archive obsolete.

### Phase 5 — CI/CD Cloud Autonomy (Medium)
Deliverables:
- `.github/workflows/agentqms-ci.yml`: on PR → validate, reindex, check-links; upload report artifact.
- `.github/workflows/agentqms-autofix.yml`: scheduled/manual → run `make fix --limit 10 --commit` on a bot branch and open PR.
Actions:
- Use `actions/setup-python` and `uv` to install dependencies; run `make` targets headlessly.
- Gate merges on a passing validation and link check.

### Phase 6 — DX Enhancements (Low)
Deliverables:
- Summaries at end of validation (violations by rule, suggested next command).
- `make commit-fixes MSG="..."` helper.
- Optional pre-commit to run `make validate` on changed docs.

## Success Criteria
- 100% validation compliance on main after migration.
- Link checker reports 0 broken links on CI for PRs.
- Auto-fix opens PRs with ≤ 10 file changes and green validation.
- Clear, specific diagnostics reduce misnaming reoccurrence (trend down over 2 weeks).

## Rollout Plan
1) Land schema + message improvements (Phases 1–2); run validate only in CI.
2) Introduce reindex + link checks; initially warn-only for one week, then enforce.
3) Enable auto-fix in bot workflow on a schedule with `--limit 10`.
4) After stability, allow maintainers to trigger larger batches with manual dispatch inputs.

## Risks & Mitigations
- False-positive link rewrites → Scope to artifacts paths only; keep backups, dry-run previews.
- Large diffs from reindex → Deterministic sorting; chunk changes via `--limit`.
- Rule regressions → Unit tests against rule schema and sample fixtures.

## Testing Strategy
- Unit tests: rule parsing, frontmatter checks, path normalization, link graph resolution.
- Integration tests: end-to-end autofix against a fixture repo; assert re-validate passes and links resolve.
- CI dry-run: run autofix without commit and compare report to expected.

## Try It (Local)
```bash
cd AgentQMS/interface
make validate
# After implementing tools:
make reindex
make check-links
make fix ARGS="--limit 10 --dry-run"
```

## Cloud Workflows (Proposed)
- PR CI: validate → reindex → check-links → upload reports; required to merge.
- Bot autofix: cron/manual → `make fix --limit 10 --commit` → push branch → open PR.

## References
- Assessment: ../assessments/2025-11-29_1810_assessment-agentqms-artifact-workflow-review.md
- Current validator: `AgentQMS/agent_tools/compliance/validate_artifacts.py`
- Interface Makefile: `AgentQMS/interface/Makefile`
