---
doc_type: reference
updated: 2025-11-28
status: current
ai_context: tech stack list
---

# Tech Stack

## Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI**: Tailwind CSS, Lucide icons
- **Editor**: Tiptap (ProseMirror)
- **State**: Zustand (sparingly), React state
- **HTTP**: Axios (see `@/lib/api.ts`)
- **Streaming**: fetch + ReadableStream
- **Standards**: See [FRONTEND_STANDARDS.md](./FRONTEND_STANDARDS.md)

## Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Validation**: Pydantic v2
- **Auth**: JWT (python-jose) via HTTPBearer
- **Agent**: LangGraph
- **LLM**: OpenAI (gpt-4o-mini default)

## Databases
- **Cache/Sessions**: Redis
- **Search**: Elasticsearch (with Nori Korean tokenizer)

## Dev Tools
- **Package**: uv (Python), npm (Node)
- **Containers**: Docker, docker-compose
- **Format**: Ruff (Python), ESLint/Prettier (TS)
- **Git**: Conventional commits

## Ports
- Frontend: 3002
- Backend: 8002
- Redis: 6379
- Elasticsearch: 9200
