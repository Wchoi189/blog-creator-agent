# AI Agent Entry Point

**🚨 READ THIS FIRST** - This is the single entry point for all AI agents working on the Blog Creator Agent migration project.

## Project Context

**Project**: Blog Creator Agent - Next.js Migration  
**Goal**: Migrate from Chainlit to Next.js + FastAPI with real-time collaborative editing  
**Status**: Migration Planning Complete, Part 1 - Foundation & Backend in progress

## Single Source of Truth

👉 **[AgentQMS AI Handbook](AgentQMS/docs/ai_handbook/)** - **Comprehensive agent protocols and guidelines**

All development rules, protocols, and instructions are in the AgentQMS AI Handbook. This file is a navigation guide.

## Quick Navigation

### Essential Reading
1. **[README.md](README.md)** - Project overview, migration vision, and quick start
2. **[AgentQMS Guide](docs/AGENTQMS_GUIDE.md)** - Framework usage, validation, and artifact management
3. **[Migration Plans](docs/plans/README.md)** - 4-part implementation roadmap

### Core Documentation

**Migration Plans** (Implementation Blueprints)
- [Part 1: Foundation & Backend](docs/plans/PART_1_FOUNDATION_AND_BACKEND.md) - FastAPI, ElasticSearch, Pydantic (3-4 weeks)
- [Part 2: Frontend Development](docs/plans/PART_2_FRONTEND_DEVELOPMENT.md) - Next.js, React, Tiptap (4 weeks)
- [Part 3: Advanced Features](docs/plans/PART_3_ADVANCED_FEATURES.md) - Yjs CRDT, GitHub publishing (3 weeks)
- [Part 4: Production Deployment](docs/plans/PART_4_PRODUCTION_DEPLOYMENT.md) - Docker, CI/CD, monitoring (2 weeks)
- [Autonomous Execution](docs/plans/AUTONOMOUS_EXECUTION_PROMPT.md) - Guidelines for autonomous agents

**Technical Assessments**
- [Migration Guide](docs/assessments/MIGRATION_GUIDE.md) - Strategic migration approach
- [Assessment V1](docs/assessments/NEXTJS_MIGRATION_ASSESSMENT.md) - Initial technical analysis
- [Assessment V2](docs/assessments/NEXTJS_MIGRATION_ASSESSMENT_V2.md) - Detailed architecture decisions

**AgentQMS Framework**
- [System Documentation](AgentQMS/docs/ai_handbook/04_agent_system/system.md) - Agent system overview
- [Protocols](AgentQMS/docs/ai_handbook/02_protocols/) - Development protocols and standards
  - [Artifact Management](AgentQMS/docs/ai_handbook/02_protocols/governance/01_artifact_management_protocol.md)
  - [Implementation Plans](AgentQMS/docs/ai_handbook/02_protocols/governance/02_implementation_plan_protocol.md)
  - [Coding Standards](AgentQMS/docs/ai_handbook/02_protocols/development/01_coding_standards_v2.md)
  - [Test Organization](AgentQMS/docs/ai_handbook/02_protocols/testing/test_organization_protocol.md)
- [References](AgentQMS/docs/ai_handbook/03_references/) - Technical references and quick guides

### AgentQMS Tools & Commands

**Makefile Commands** (recommended - run from `AgentQMS/agent_interface/`)
```bash
cd AgentQMS/agent_interface

# Discovery and status
make discover           # List all available tools
make status            # Check system status

# Artifact management
make create-plan       # Create implementation plan
make create-assessment # Create technical assessment
make create-design     # Create design document

# Validation and compliance
make validate          # Validate all artifacts
make validate-file     # Validate specific file
make compliance        # Check compliance status
make boundary          # Validate framework boundaries

# Documentation
make docs-generate     # Generate documentation indexes
make docs-validate-links  # Check for broken links
make docs-update-indexes  # Update artifact indexes
```

**Python Tools** (direct execution)
```bash
# Artifact workflow
python AgentQMS/agent_tools/core/artifact_workflow.py create --type implementation_plan --name feature --title "Feature Name"

# Validation
python AgentQMS/agent_tools/compliance/validate_artifacts.py --all
python AgentQMS/agent_tools/compliance/validate_artifacts.py --file docs/plans/PART_1.md

# Documentation
python AgentQMS/agent_tools/documentation/auto_generate_index.py --validate
python AgentQMS/agent_tools/documentation/validate_links.py

# Discovery
python AgentQMS/agent_tools/core/discover.py
```

### Project Structure Reference

```
blog-creator-agent/
├── AgentQMS/              # Quality management framework
│   ├── agent_interface/   # CLI commands (Makefile)
│   ├── agent_tools/       # Automation scripts
│   └── docs/ai_handbook/  # Agent protocols
├── docs/
│   ├── plans/             # Implementation plans (Part 1-4)
│   ├── assessments/       # Technical assessments
│   └── AGENTQMS_GUIDE.md  # Framework usage guide
├── src/                   # Legacy Python source
│   ├── agent.py           # BlogContentAgent (LangGraph)
│   ├── graph.py           # State machine
│   ├── retriever.py       # RAG retriever
│   └── ui/chainlit/       # Legacy Chainlit UI
├── configs/               # Application configuration
├── prompts/               # LLM prompts
└── README.md              # Project overview
```

## Development Workflow

### Starting a New Task

1. **Read the relevant implementation plan** in `docs/plans/`
2. **Check AgentQMS protocols** for standards and guidelines
3. **Use AgentQMS tools** to create artifacts if needed
4. **Validate your work**: `make validate` and `make compliance`

### Creating New Documentation

1. Use AgentQMS templates: `make create-plan` or `make create-assessment`
2. Follow frontmatter requirements (title, date, status, tags)
3. Use semantic filenames (not timestamps)
4. Validate before committing: `make validate-file FILE=path/to/file.md`

### Code Development

1. **Legacy codebase** (`src/`): Python with LangChain/LangGraph - currently operational
2. **Migration target**: Next.js 14 + FastAPI (see implementation plans)
3. Follow coding standards in `AgentQMS/docs/ai_handbook/02_protocols/development/`
4. Keep RAG pipeline and agent logic - only replacing UI/infrastructure

## Key Principles

**Migration Philosophy**
- Preserve proven RAG pipeline and LangGraph agent logic
- Replace chat UI with document-centric collaborative editing
- Add real-time multi-user support with Yjs CRDT
- Production-ready infrastructure (ElasticSearch, Docker, CI/CD)

**Documentation Standards**
- All artifacts have YAML frontmatter (title, date, status)
- Semantic filenames, not timestamps
- Validate with AgentQMS before committing
- Keep implementation plans updated with progress

**Quality Management**
- Use AgentQMS for artifact creation and validation
- Follow established protocols in AI Handbook
- Run compliance checks regularly
- Maintain consistency across documentation

---

**Remember**:
- Read implementation plans in `docs/plans/` for detailed task breakdowns
- Use AgentQMS tools for artifact management and validation
- Consult AI Handbook (`AgentQMS/docs/ai_handbook/`) for protocols
- See `docs/AGENTQMS_GUIDE.md` for complete framework documentation