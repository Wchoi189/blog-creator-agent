---
doc_type: api
updated: 2025-11-27
status: current
ai_context: backend endpoints reference
---

# API Endpoints

**Base**: `http://localhost:8002`

## Authentication

All protected endpoints require a JWT token via the `Authorization` header:

```
Authorization: Bearer <access_token>
```

**Important:** The backend does NOT read tokens from cookies. Even with `credentials: 'include'`, you must explicitly set the `Authorization` header.

### Client-Side Authentication

- Use the axios client from `@/lib/api` which automatically attaches the token via interceptor
- For streaming/special cases, use `authorizedFetch` or manually add the header
- The token is available via `getClientToken()` which reads from the `client_token` cookie

### Token Flow

1. User logs in via `/api/v1/auth/login`
2. Backend sets both `access_token` (httpOnly) and `client_token` (accessible) cookies
3. Client-side code reads `client_token` and includes it as `Authorization: Bearer` header
4. Axios interceptor in `api.ts` handles this automatically
5. Raw `fetch` calls must manually add the header using `getClientToken()`

## Auth Endpoints
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
- `ws://localhost:8002/ws?token={jwt}` - Real-time updates
