# Blog Creator Agent - CONTINUE.md Guide

## Project Overview

**Blog Creator Agent** is a RAG-powered system that transforms documents (PDFs, audio, images) into blog posts using AI assistance. It features real-time collaborative editing with multi-user support.

### Key Technologies
- **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Tiptap (rich text editor), Yjs (CRDT for collaboration), Zustand, SWR
- **Backend**: FastAPI, Python 3.11, LangChain/LangGraph, OpenAI/Ollama, Redis (cache/sessions), Elasticsearch (search)
- **Document Processing**: PyMuPDF (PDF), audio transcription, vision models
- **Other**: uv (Python deps), Ruff (linter), pre-commit, pytest, Docker for services

### High-level Architecture
- **Frontend**: Handles UI, collaborative editor, API calls via Axios
- **Backend**: REST APIs, WebSockets for real-time, LangGraph agents for content generation
- **Data Flow**: Upload docs → Process/index → Agent generates blog → Collaborative edit → Publish (Jekyll/GitHub)

See detailed Mermaid diagram in [README.md](README.md).

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- uv (fast Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Docker (for Redis/Elasticsearch)

### Installation
1. **Backend**:
   ```
   uv sync  # Install deps from pyproject.toml
   cp backend/.env.example backend/.env  # Add API keys (OPENAI_API_KEY, TAVILY_API_KEY, etc.)
   uv run python -m backend.main  # or uvicorn backend.main:app --reload
   ```
   Runs on http://localhost:8000 (API docs at /docs)

2. **Frontend**:
   ```
   cd frontend
   npm install
   cp .env.local.example .env.local  # Set NEXT_PUBLIC_API_URL=http://localhost:8000
   npm run dev
   ```
   Runs on http://localhost:3002

3. **Services** (optional):
   ```
   docker run -d -p 6379:6379 redis/redis-stack:latest
   # Elasticsearch: use Docker or install locally
   ```

### Basic Usage
- Login/Register (JWT auth)
- Upload documents
- Generate blog draft using RAG agent
- Edit collaboratively in Tiptap editor
- Publish to GitHub (upcoming)

### Running Tests
```
# Backend
pytest backend/tests/

# Frontend
cd frontend && npm test  # or add test script
```

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── main.py          # Entry point
│   ├── api/v1/          # Endpoints: auth, documents, blog, sessions, websocket
│   ├── services/        # Business logic (auth, document, blog, session)
│   ├── models/          # Pydantic schemas
│   ├── agent/           # LangGraph workflows
│   ├── core/            # Config, security
│   └── tests/
├── frontend/             # Next.js app
│   ├── src/
│   │   ├── app/         # Routes: auth, dashboard
│   │   ├── components/  # UI: editor, layout
│   │   ├── lib/         # Utils, API client
│   │   ├── hooks/
│   │   └── store/       # Zustand stores
│   ├── next.config.js
│   └── tailwind.config.ts
├── AgentQMS/            # Agent Quality Management System toolkit
│   ├── agent_tools/     # Audit, compliance, docs tools
│   ├── toolkit/         # Utilities, CLI
│   ├── interface/       # CLI tools
│   └── conventions/     # Coding standards
├── docs/                # Detailed guides, plans
├── pyproject.toml       # Python deps (hatchling build)
├── .venv/               # Virtual env (uv)
└── README.md            # Main docs
```

**Key Config Files**:
- `backend/.env`: API keys, DB URLs
- `frontend/.env.local`: NEXT_PUBLIC_API_URL
- `pyproject.toml`: Backend deps
- `frontend/package.json`: Frontend deps

## Development Workflow

### Coding Standards
- **Python**: Ruff (linter/formatter), mypy (types), pre-commit hooks
- **TypeScript**: ESLint, Next.js lint
- Use Pydantic models for validation
- Type hints everywhere (Python/TS)
- Follow conventions in `AgentQMS/conventions/`

### Testing
- Backend: pytest with pytest-asyncio
- Frontend: Jest/React Testing Library (add as needed)
- Run `pre-commit install` for hooks

### Build & Deployment
- **Dev**: `uv sync` (backend), `npm i` (frontend)
- **Build Backend**: `hatch build` (wheels)
- **Build Frontend**: `npm run build` → standalone in `.next/standalone`
- **Deploy**: Dockerize (pending), Vercel (frontend), Railway/Heroku (backend)

### Contribution Guidelines
1. Fork/branch: `feat/xyz`, `fix/xyz`
2. `pre-commit run --all-files`
3. Update tests
4. PR with changelog

## Key Concepts

- **RAG Pipeline**: Retrieve from ES/Redis, augment LLM prompts
- **LangGraph Agent**: Stateful graph for blog generation (router, tools: doc search, web search)
- **Yjs CRDT**: Conflict-free real-time collaboration
- **WebSocket Streaming**: LLM responses stream to editor
- **Document Types**: PDF (PyMuPDF), Audio (transcribe), Images (vision)
- **Auth**: JWT for sessions, API keys for agents

## Common Tasks

### 1. Start Development Servers
```
# Terminal 1: Backend
uv run python -m backend.main

# Terminal 2: Frontend
cd frontend && npm run dev
```

### 2. Add New API Endpoint
```
backend/api/v1/new_endpoint.py
# Add route in main.py
# Add service/model
# Test with pytest
```

### 3. Update LangGraph Agent
```
backend/agent/src/  # Edit graphs, nodes
uv run python -m backend.agent.graphs.blog_creator
```

### 4. Process a Document
```
curl -X POST http://localhost:8000/api/v1/documents/ \
  -H "Authorization: Bearer <token>" \
  -F "file=@doc.pdf"
```

### 5. Run AgentQMS Audit
```
cd AgentQMS
python -m toolkit.audit.checklist_tool  # Example
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **CORS errors** | Check `backend/core/cors.py`, frontend NEXT_PUBLIC_API_URL |
| **LangChain import errors** | `uv sync --dev`, check versions |
| **Redis connection** | Verify Docker `docker ps`, env REDIS_URL |
| **ES indexing fails** | Check ES health `/health`, Nori tokenizer |
| **Editor not syncing** | WebSocket connection, Yjs provider |
| **API 422 errors** | Validate Pydantic models |
| **Tests fail** | `pytest -v --asyncio-mode=auto` |

**Debug Tips**:
- Backend: `uvicorn --log-level debug`
- Frontend: Next.js dev tools
- Redis: `redis-cli monitor`
- ES: Kibana dev tools

## References
- [Main README.md](README.md)
- [Installation Guide](docs/1_INSTALLATION.md)
- [Architecture Docs](docs/3_ARCHITECTURE.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Yjs](https://docs.yjs.dev/)
- [Tiptap](https://tiptap.dev/)

**AgentQMS**: Use for agent auditing/compliance. See `AgentQMS/README.md` (if exists) or `CHANGELOG.md`.

---

*Generated by AI Assistant. Review and customize as needed. Continue auto-loads this into context.*
