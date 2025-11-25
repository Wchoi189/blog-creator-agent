---
doc_type: architecture
updated: 2025-11-24-1830
status: current
ai_context: system architecture diagram
---

# Architecture

```
┌─────────────────┐
│   Next.js 14    │ Frontend (Port 3000)
│  - React 18     │ - Auth: Zustand + JWT
│  - Tiptap       │ - UI: Tailwind CSS
│  - TypeScript   │ - SSE streaming
└────────┬────────┘
         │ HTTP/WS
┌────────▼────────┐
│   FastAPI       │ Backend (Port 8000)
│  - Python 3.11  │ - JWT auth
│  - Pydantic     │ - REST + WebSocket
└────────┬────────┘
         │
    ┌────┴────┬────────┬──────────┐
    │         │        │          │
┌───▼───┐ ┌──▼──┐ ┌───▼────┐ ┌──▼────┐
│ Redis │ │Chroma│ │Elastic │ │LangGraph│
│Cache  │ │Vector│ │Search  │ │ Agent  │
└───────┘ └──────┘ └────────┘ └────────┘
                                   │
                              ┌────▼────┐
                              │ OpenAI  │
                              │ Claude  │
                              └─────────┘
```

## Data Flow

**Upload**: User → Next.js → FastAPI → File Storage → Process Job → Vectorize → ChromaDB
**Generate**: User selects docs → FastAPI → LangGraph → RAG search → LLM → Stream → Next.js
**Edit**: TiptapEditor → Auto-save → FastAPI → Update DB
**Refine**: Feedback → SSE stream → LangGraph → Real-time tokens → Editor

## Key Paths

- `frontend/src/app/(dashboard)/` - Protected pages
- `backend/api/v1/` - REST routes
- `backend/agent/` - LangGraph workflow
- `backend/services/` - Business logic
