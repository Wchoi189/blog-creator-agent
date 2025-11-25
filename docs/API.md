---
doc_type: api
updated: 2025-11-24-1830
status: current
ai_context: backend endpoints reference
---

# API Endpoints

**Base**: `http://localhost:8000`

## Auth
- `POST /api/v1/auth/register` - Create user
- `POST /api/v1/auth/login` - Get JWT token
- `GET /api/v1/auth/me` - Current user
- `POST /api/v1/auth/api-keys` - Create API key
- `GET /api/v1/auth/api-keys` - List keys
- `DELETE /api/v1/auth/api-keys/{id}` - Revoke key

## Documents
- `POST /api/v1/documents/upload` - Upload file (multipart)
- `GET /api/v1/documents` - List all
- `GET /api/v1/documents/{id}` - Get one
- `DELETE /api/v1/documents/{id}` - Delete
- `POST /api/v1/documents/{id}/process` - Trigger vectorization
- `POST /api/v1/documents/search` - RAG search

## Blog
- `POST /api/v1/blog/generate` - Generate draft (LangGraph agent)
- `GET /api/v1/blog` - List drafts
- `GET /api/v1/blog/{id}` - Get draft
- `PUT /api/v1/blog/{id}` - Update draft
- `DELETE /api/v1/blog/{id}` - Delete draft
- `POST /api/v1/blog/{id}/generate-content` - Regenerate
- `GET /api/v1/blog/{id}/refine?feedback=` - SSE streaming refinement
- `POST /api/v1/blog/{id}/export` - Export markdown

## Sessions
- `POST /api/v1/sessions` - Create session
- `GET /api/v1/sessions` - List all
- `GET /api/v1/sessions/{id}` - Get one
- `DELETE /api/v1/sessions/{id}` - Delete
- `GET /api/v1/sessions/{id}/chat-history` - Message history

## WebSocket
- `ws://localhost:8000/ws?token={jwt}` - Real-time updates

**Auth**: Bearer token in `Authorization` header
