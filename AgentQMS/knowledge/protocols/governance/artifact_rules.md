---
title: "Artifact Rules for AI Agents"
audience: agent
status: active
domain: governance
id: PROTO-GOV-ARTIFACT-RULES
---

## When This Applies

- You are creating, updating, or regenerating any quality-management artifact.
- You are naming or placing files under the artifacts directory tree.
- You are generating templates or protocol-based documents for the framework.

## Rules

- **File naming**: Always use `YYYY-MM-DD_HHMM_[PREFIX]_descriptive-name.md`.
- **Directory placement**:
  - Templates → `templates/`
  - Implementation plans → `implementation_plans/`
  - Assessments → `assessments/`
  - Audits → `audits/`
  - Research → `research/`
  - Design docs → `design_documents/`
  - Bug reports → `bug_reports/`
- **Frontmatter**: Always include structured frontmatter with:
  - `title`, `date`, `type`, `category`, `status`, `version`, and `tags`.
- **Naming conventions**:
  - Use kebab-case for the descriptive-name segment.
  - Use clear, semantic names; avoid generic terms like `test`, `tmp`, `misc`.
- **Automation first**:
  - Prefer artifact generators and workflows over manual file creation.
  - If a generator exists for a type, use it instead of writing the file from scratch.

## Common Mistakes

- Creating artifacts with timestamps only or non-semantic names.
- Placing artifacts directly under `docs/` or project root instead of the correct subdirectory.
- Omitting required frontmatter fields or leaving `status`/`version` blank.
- Using mixed or inconsistent naming styles (camelCase, spaces) instead of kebab-case.

## Related

- `AgentQMS/conventions/q-manifest.yaml` – authoritative list of artifact types, schemas, templates, and locations.
- Bug Fix Protocol (`PROTO-GOV-004`) – bug-report documentation and follow-up expectations.


