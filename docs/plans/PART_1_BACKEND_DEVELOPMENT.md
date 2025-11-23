# Part 1: Backend Development (FastAPI)

## Status: 🔄 In Progress (0%)

**Goal**: Build a complete FastAPI backend that replicates all Chainlit functionality as REST/WebSocket APIs.

## Architecture Overview

```
backend/
├── __init__.py
├── main.py                 # FastAPI app entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── models/                # Pydantic models
│   ├── __init__.py
│   ├── auth.py           # Auth models (User, Token, APIKey)
│   ├── documents.py      # Document models
│   ├── blog.py           # Blog generation models
│   └── sessions.py       # Session models
├── api/                   # API routes
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── auth.py       # /api/v1/auth/*
│   │   ├── documents.py  # /api/v1/documents/*
│   │   ├── blog.py       # /api/v1/blog/*
│   │   ├── sessions.py   # /api/v1/sessions/*
│   │   └── websocket.py  # WebSocket endpoint
│   └── dependencies.py   # Shared dependencies
├── services/             # Business logic
│   ├── __init__.py
│   ├── auth_service.py
│   ├── document_service.py
│   ├── blog_service.py
│   └── session_service.py
├── core/                 # Core utilities
│   ├── __init__.py
│   ├── security.py       # JWT, password hashing
│   ├── database.py       # DB connections
│   └── middleware.py     # Custom middleware
├── agent/               # LangGraph agent (reused from src/)
│   ├── __init__.py
│   ├── agent.py         # BlogContentAgent
│   ├── graph.py         # LangGraph implementation
│   └── tools.py         # Agent tools
└── tests/              # Test suite
    ├── __init__.py
    ├── test_auth.py
    ├── test_documents.py
    └── test_blog.py
```

## Phase 1.1: Project Setup (CURRENT)

### Task 1.1.1: Initialize FastAPI Project ✅

**Objective**: Create backend directory structure and core files

**Actions**:
1. Create `backend/` directory
2. Setup `main.py` with FastAPI app
3. Create directory structure as shown above
4. Initialize `__init__.py` files

**Files to create**:
- `backend/main.py` - FastAPI app with CORS, middleware
- `backend/config.py` - Environment configuration
- `backend/requirements.txt` - Dependencies

**Dependencies needed**:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
sqlalchemy==2.0.23
elasticsearch==8.11.0
redis==5.0.1
python-dotenv==1.0.0
langchain==0.1.0
langchain-openai==0.0.2
langgraph==0.0.30
tavily-python==0.3.0
```

### Task 1.1.2: Setup Configuration Management

**Objective**: Create centralized configuration using Pydantic Settings

**Files**:
- `backend/config.py`

**Configuration sections**:
- App settings (name, version, debug)
- CORS origins
- Database URLs (ElasticSearch, Redis, ChromaDB)
- JWT settings (secret, algorithm, expiration)
- LLM settings (provider, model, API keys)
- Upload settings (max file size, allowed extensions)

### Task 1.1.3: Setup Database Connections

**Objective**: Initialize ElasticSearch and ChromaDB clients

**Files**:
- `backend/core/database.py`

**Features**:
- ElasticSearch client with fallback to ChromaDB
- Connection pooling
- Health check functions
- Automatic retry logic

## Phase 1.2: Authentication & Security

### Task 1.2.1: Implement JWT Authentication

**Objective**: Create JWT-based auth system

**Files**:
- `backend/core/security.py` - JWT utilities
- `backend/models/auth.py` - User, Token models
- `backend/api/v1/auth.py` - Auth endpoints

**Endpoints**:
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - Login (returns JWT)
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

**Security features**:
- Password hashing with bcrypt
- JWT token generation and validation
- Token expiration (15min access, 7d refresh)
- Secure password requirements

### Task 1.2.2: Implement API Key Management

**Objective**: Alternative authentication via API keys

**Files**:
- `backend/api/v1/auth.py` (extend)

**Endpoints**:
- `POST /api/v1/auth/api-keys` - Create API key
- `GET /api/v1/auth/api-keys` - List user's API keys
- `DELETE /api/v1/auth/api-keys/{key_id}` - Revoke API key

**Features**:
- Generate secure API keys
- Store hashed keys only
- Key expiration support
- Usage tracking

### Task 1.2.3: Add Rate Limiting

**Objective**: Protect API from abuse

**Files**:
- `backend/core/middleware.py`

**Features**:
- Rate limiting per IP/user
- Different limits for different endpoints
- Redis-based counter storage
- Clear error messages when limit exceeded

## Phase 1.3: Core API Endpoints

### Task 1.3.1: Health & Metrics Endpoints

**Endpoints**:
- `GET /health` - Service health check
- `GET /metrics` - Prometheus metrics
- `GET /api/v1/status` - Detailed system status

### Task 1.3.2: Document Upload & Processing

**Files**:
- `backend/models/documents.py`
- `backend/services/document_service.py`
- `backend/api/v1/documents.py`

**Endpoints**:
- `POST /api/v1/documents/upload` - Upload file (PDF, audio, image)
- `GET /api/v1/documents` - List user's documents
- `GET /api/v1/documents/{doc_id}` - Get document details
- `DELETE /api/v1/documents/{doc_id}` - Delete document
- `POST /api/v1/documents/{doc_id}/process` - Process document

**Features**:
- Multi-file upload support
- File type validation (PDF, MP3, PNG, JPG)
- Chunking and vectorization
- Progress tracking
- Reuse `src/document_preprocessor.py` logic

### Task 1.3.3: RAG Query Endpoints

**Files**:
- `backend/api/v1/documents.py` (extend)

**Endpoints**:
- `POST /api/v1/documents/search` - Semantic search
- `POST /api/v1/documents/query` - RAG query

**Features**:
- Vector similarity search
- Hybrid search (ElasticSearch + vector)
- Relevance scoring
- Source attribution

### Task 1.3.4: Blog Generation Endpoints

**Files**:
- `backend/models/blog.py`
- `backend/services/blog_service.py`
- `backend/api/v1/blog.py`

**Endpoints**:
- `POST /api/v1/blog/generate` - Generate blog draft
- `PUT /api/v1/blog/{draft_id}` - Update draft
- `POST /api/v1/blog/{draft_id}/refine` - Refine with agent
- `GET /api/v1/blog/{draft_id}` - Get draft
- `POST /api/v1/blog/{draft_id}/export` - Export to markdown
- `POST /api/v1/blog/{draft_id}/publish` - Publish to GitHub

**Features**:
- Streaming responses (SSE)
- Draft versioning
- Undo/redo support
- Markdown export

### Task 1.3.5: Session Management

**Files**:
- `backend/models/sessions.py`
- `backend/services/session_service.py`
- `backend/api/v1/sessions.py`

**Endpoints**:
- `POST /api/v1/sessions` - Create session
- `GET /api/v1/sessions` - List sessions
- `GET /api/v1/sessions/{session_id}` - Get session
- `DELETE /api/v1/sessions/{session_id}` - Delete session

**Features**:
- Session state management
- Chat history persistence
- Session metadata (documents, drafts)

## Phase 1.4: Agent Integration

### Task 1.4.1: Port LangGraph Agent

**Objective**: Integrate existing LangGraph agent into FastAPI

**Files**:
- `backend/agent/agent.py` (copy from `src/agent.py`)
- `backend/agent/graph.py` (copy from `src/graph.py`)
- `backend/agent/tools.py` (copy from `src/agent_tool.py`)

**Changes needed**:
- Update imports to work with FastAPI structure
- Add async support where needed
- Integrate with FastAPI dependency injection

### Task 1.4.2: Implement Streaming Responses

**Objective**: Stream LLM responses in real-time

**Files**:
- `backend/api/v1/blog.py` (extend)

**Features**:
- Server-Sent Events (SSE) for streaming
- Token-by-token streaming
- Progress updates
- Error handling during streaming

### Task 1.4.3: Add WebSocket Support

**Objective**: Real-time bidirectional communication

**Files**:
- `backend/api/v1/websocket.py`

**Features**:
- WebSocket endpoint `/ws/{session_id}`
- Connection management
- Message broadcasting
- Heartbeat/ping-pong

## Testing Strategy

### Unit Tests
- Test each service independently
- Mock external dependencies (LLM, DB)
- Aim for 90%+ coverage

### Integration Tests
- Test API endpoints end-to-end
- Use TestClient from FastAPI
- Test auth flows

### Performance Tests
- Load testing with locust
- Measure response times
- Identify bottlenecks

## API Documentation

FastAPI auto-generates:
- **OpenAPI spec**: `/openapi.json`
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## Environment Variables

Required in `.env`:
```bash
# App
APP_NAME="Blog Creator API"
APP_VERSION="1.0.0"
DEBUG=false

# Security
SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Database
ELASTICSEARCH_URL="http://localhost:9200"
REDIS_URL="redis://localhost:6379"
CHROMADB_PATH="./data/chromadb"

# LLM
OPENAI_API_KEY="sk-..."
TAVILY_API_KEY="tvly-..."

# CORS
CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
```

## Next Steps

After completing Part 1:
1. Update progress in `docs/plans/README.md`
2. Commit changes with message: "feat: complete FastAPI backend (Part 1)"
3. Push to branch
4. Begin Part 2 (Frontend Development)

## Success Criteria

- ✅ All 20+ endpoints implemented
- ✅ Authentication working (JWT + API keys)
- ✅ Document processing functional
- ✅ Blog generation working
- ✅ Streaming responses operational
- ✅ WebSocket connection stable
- ✅ Tests passing (90%+ coverage)
- ✅ API documentation complete
