---
title: "AI Agent System – Single Source of Truth"
date: "2025-10-29 00:00 (KST)"
type: "guide"
category: "ai_agent"
status: "active"
version: "1.0"
tags: ["ai_agent", "rules", "operations"]
---

AI Agent System – Single Source of Truth
=======================================

Status: ACTIVE

Read this file only. Agents do not need tutorials.

Core Rules
----------
- Always use automation tools; never create files manually.
- No loose docs in project root; no ALL CAPS filenames (except README.md, CHANGELOG.md).
- Use kebab/underscore naming with timestamp prefix.
- Test in browser and check logs; do not rely on unit tests alone.

Artifact Creation (use one of these)
------------------------------------
```bash
# From agent interface (recommended)
cd AgentQMS/interface/
make create-plan NAME=my-plan TITLE="My Plan"
make create-assessment NAME=my-assessment TITLE="My Assessment"
make create-design NAME=my-design TITLE="My Design"
make create-bug-report NAME=my-bug TITLE="My Bug Report"
```

Types: implementation_plan, assessment, design, research, template, bug_report

**Implementation Plans**: Always use Blueprint Protocol Template (PROTO-GOV-003). The generator uses this template automatically. See `AgentQMS/knowledge/templates/blueprint_protocol_template.md` for structure.

Tool Discovery and Validation
-----------------------------
```bash
# Agent tools (run inside AgentQMS/interface/)
cd AgentQMS/interface/
make help
make discover
make status
make validate
make compliance
```

Documentation Organization
--------------------------
- Artifacts live under `artifacts/` by type.
- Required frontmatter and naming: `YYYY-MM-DD_HHMM_[type]_descriptive-name.md`.
- Frontmatter `date` must use the full timestamp format `YYYY-MM-DD HH:MM (KST)` for every commit.
- Long-form guidance lives in `AgentQMS/knowledge/` (not for agents).
- Agent doc map: see `AgentQMS/knowledge/agent/` index (SST + quick references).
- Tracking domain: `AgentQMS/knowledge/agent/tracking_cli.md` and related references.
- Automation domain: `AgentQMS/knowledge/agent/tool_catalog.md` and automation references.
- Coding and development protocols: `AgentQMS/knowledge/protocols/development/`.
- Escalation: if any knowledge domain exceeds a manageable size, adopt capability-based indexing using `.agentqms/state/architecture.yaml` and metadata (`capabilities`, `audience`, `visibility`).
- This file is the sole authoritative agent instruction.

Documentation Style for AI Agents
----------------------------------
When creating/updating AI-oriented instructions:
- ✅ Provide concise hints/reminders (1-3 lines max per concept)
- ✅ Show minimal code examples (correct/incorrect patterns)
- ✅ Use bullet points, not paragraphs
- ❌ No tutorials or comprehensive explanations
- ❌ No multi-paragraph descriptions
- ❌ No redundant context

Agents don't need tutorials - minimal hints are sufficient. Verbose docs consume context and reduce effectiveness.

Path Management
---------------
ALWAYS use path_utils for sys.path setup:
```python
from streamlit_app.utils.path_utils import setup_project_paths
setup_project_paths()
```

NEVER manually manipulate sys.path:
```python
# ❌ WRONG
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
```

Loader registry path issues: Use `LOADER_BASE_PATH` env var if needed. See `AgentQMS/knowledge/references/development/loader_path_resolution.md`.

Do / Don't
----------
Do:
- Use `artifact_workflow.py` for all artifacts
- Follow naming + frontmatter
- Update indexes when prompted
- Use `scripts/utilities/process_manager.py` to view logs
- Use `setup_project_paths()` for all path setup
- Use `width="stretch"` or `width="content"` for Streamlit charts/tables/buttons (not `use_container_width`)

Don't:
- Create or edit artifacts manually
- Place docs in project root
- Add try/except that hide errors
- Modify core schema engine files without full-browser testing
- Manually manipulate sys.path (use path_utils instead)
- Write verbose tutorials in AI instruction files (use concise hints)
- Use `use_container_width` in Streamlit (deprecated - use `width="stretch"` or `width="content"`)

Operational Commands
--------------------
```bash
make run
make stop
make status
python scripts/utilities/process_manager.py logs --port 8501 --lines 100
```

File Impact (test scope)
------------------------
- schema YAML/page wrappers: test that page in browser
- renderer factory/engine core: test ALL pages
- services/utils: test affected pages

When Stuck
----------
- Re-run discovery/validate
- Check logs and browser
- Read `.ai-context.md` for architecture context

Streamlit API Rules
-------------------
- NEVER use `use_container_width` parameter (deprecated after 2025-12-31)
- ALWAYS use `width="stretch"` instead of `use_container_width=True`
- ALWAYS use `width="content"` instead of `use_container_width=False`
- Applies to: `st.plotly_chart()`, `st.dataframe()`, `st.button()`, all chart/table components
- Look for inline comments "CRITICAL: NEVER pass use_container_width" at call sites
- Assertions will fail if deprecated parameter is used - this is intentional


