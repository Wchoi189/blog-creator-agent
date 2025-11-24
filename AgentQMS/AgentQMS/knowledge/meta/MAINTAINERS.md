---
title: "AgentQMS Maintainers Guide"
audience: maintainer
status: draft
version: "0.1"
---

## Purpose

- Provide a concise, container-focused guide for maintaining and exporting AgentQMS.
- Assume the framework is used as a reusable bundle: `.agentqms/` + `AgentQMS/`.

## Key Locations

- `.agentqms/` – runtime state and effective configuration (including `state/architecture.yaml`).
- `AgentQMS/agent_tools/` – implementation layer (Python tools).
- `AgentQMS/conventions/` – artifact types, schemas, templates, audit framework.
- `AgentQMS/knowledge/` – agent instructions, protocols, references, templates, meta docs.

## Export & Adaptation (High Level)

- Copy `.agentqms/` and `AgentQMS/` into the target project.
- Optionally create a project-level `config/` to override framework defaults.
- Run basic checks:
  - `cd AgentQMS/interface && make discover`
  - `make status`
  - `make validate`

## Legacy Project Docs

- Long-form export guides and historical assessments under `docs/` are **project history**, not part of the reusable container.
- When packaging AgentQMS for reuse, exclude:
  - `docs/export_guide.md`
  - `docs/quick_start_export.md`
  - `docs/resources.md`
  - Project-specific artifacts and RFCS.


