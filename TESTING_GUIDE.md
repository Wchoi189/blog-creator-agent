# Testing Guide - Blog Creator Application

## Quick Start

### Prerequisites
```bash
# Ensure all services are running
redis-server --daemonize yes
make s  # Start backend and frontend
```

### Test User Credentials
- Email: `browser_test@example.com` or `test@example.com`
- Password: `TestPass123`

## API Testing (curl)

### 1. Authentication Flow
```bash
# Register
curl -X POST http://localhost:8002/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123","full_name":"Test User"}'

# Login (save token for next requests)
TOKEN=$(curl -s -X POST http://localhost:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}' | jq -r '.access_token')

# Verify current user
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/api/v1/auth/me
```

### 2. Document Upload
```bash
# Create a test PDF (or use existing one)
# Upload document
curl -X POST "http://localhost:8002/api/v1/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf"

# List documents
curl "http://localhost:8002/api/v1/documents" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Blog Generation
```bash
# Create session
SESSION=$(curl -s -X POST http://localhost:8002/api/v1/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Session"}' | jq -r '.id')

# Get document ID from previous list
DOC_ID="798d9047-8a2d-42b2-8956-c73760052e20"

# Generate draft
curl -X POST "http://localhost:8002/api/v1/blog/generate?session_id=$SESSION" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"document_ids\":[\"$DOC_ID\"],\"title\":\"Test Blog\"}"

# List drafts
curl "http://localhost:8002/api/v1/blog" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Draft Editing
```bash
# Get draft ID from previous list
DRAFT_ID="ecfadedf-07f0-49fa-bfa1-f2eec33f1745"

# Update draft content
curl -X PUT "http://localhost:8002/api/v1/blog/$DRAFT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Updated blog content","title":"Updated Title"}'

# Export as markdown
curl "http://localhost:8002/api/v1/blog/$DRAFT_ID/export" \
  -H "Authorization: Bearer $TOKEN" > draft.md
```

## Frontend Testing (Browser)

### Login Page
- Navigate to: http://localhost:3002/login
- Test registration and login flows
- Verify token persistence on page refresh

### Upload Page
- Navigate to: http://localhost:3002/dashboard/upload
- Test "Browse Files" button
- Test drag-and-drop upload
- Verify redirect to documents after upload

### Documents Page
- Navigate to: http://localhost:3002/dashboard/documents
- Verify uploaded documents appear
- Check file metadata (size, type, status)
- Test document deletion

### Blog Generation Page
- Navigate to: http://localhost:3002/dashboard/generate
- Select documents
- Generate draft
- Verify redirect to drafts page

### Drafts/Editor Page
- Navigate to: http://localhost:3002/dashboard/drafts
- View all drafts
- Click draft to open editor
- Test Tiptap editor functionality
- Test save changes
- Verify updates persist

## File Types Supported
- **PDF**: `.pdf`
- **Audio**: `.mp3`, `.wav`, `.m4a`

## Known Limitations

### Current
- No AI content generation implemented (streaming endpoints prepared but need LLM integration)
- No collaborative editing (Yjs CRDT prepared for Part 3)
- No GitHub publishing (prepared for Part 3)

### Testing Considerations
- Document processing takes ~3 seconds (background task)
- Each test creates new database entries (use unique emails)
- Redis must be running before backend starts
- API tokens expire after ~24 hours (refresh_token available but not implemented in frontend yet)

## Troubleshooting

### Services not responding
```bash
# Check Redis
redis-cli ping

# Check backend health
curl http://localhost:8002/health

# Check frontend
curl http://localhost:3002 | head -20
```

### Upload fails with "Unsupported file type"
- Only .pdf, .mp3, .wav, .m4a are accepted
- Check file extension case sensitivity

### Auth token invalid
- Tokens expire after ~24 hours
- Create new token via login endpoint
- Frontend handles 401 errors by redirecting to login

### CORS errors in browser
- Check backend CORS configuration in `backend/main.py`
- Ensure frontend URL (3002) is in allowed origins

## Performance Notes
- Document upload: <1 second
- Document processing: ~3 seconds
- Draft creation: <1 second
- Draft update: <1 second
- Redis operations: <100ms

## Next Steps for Full Testing

1. **AI Content Generation** (requires LLM integration)
   - POST /api/v1/blog/{draft_id}/generate-content (streaming)
   - POST /api/v1/blog/{draft_id}/refine (streaming with feedback)

2. **Collaborative Editing** (Yjs CRDT implementation)
   - WebSocket endpoint for real-time collaboration
   - Conflict resolution and operational transformation

3. **GitHub Publishing** (API integration)
   - GitHub OAuth flow
   - Repository creation/update
   - GitHub Pages deployment

4. **Advanced Features**
   - Document search/filtering
   - Draft version history
   - Export to multiple formats (HTML, EPUB, etc.)
   - Analytics dashboard
