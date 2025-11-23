# Part 3: Advanced Features

## Status: ⏸️ Pending (0%)

**Goal**: Implement real-time collaboration with Yjs CRDT and automated GitHub publishing.

## Phase 3.1: Yjs CRDT Integration

### Overview

**Yjs** (pronounced "why-js") is a CRDT (Conflict-free Replicated Data Type) library that enables real-time collaborative editing without conflicts. It's used by Notion, Figma, and other modern collaboration tools.

### Task 3.1.1: Setup Yjs Backend Provider

**Objective**: Create WebSocket server for Yjs synchronization

**Files**:
- `backend/services/yjs_service.py` - Yjs document management
- `backend/api/v1/yjs.py` - Yjs WebSocket endpoint

**Features**:
- Persistent Y.Doc storage (Redis or filesystem)
- Multi-client synchronization
- Document awareness (who's online)
- Automatic garbage collection

**Implementation**:
```python
# backend/api/v1/yjs.py
from fastapi import WebSocket, WebSocketDisconnect
from ypy_websocket import WebsocketServer, WebsocketProvider

class YjsWebSocketHandler:
    def __init__(self):
        self.rooms = {}  # document_id -> YDoc
        self.connections = {}  # document_id -> [WebSocket]

    async def handle_connection(
        self,
        websocket: WebSocket,
        document_id: str
    ):
        await websocket.accept()

        # Get or create Y.Doc
        if document_id not in self.rooms:
            self.rooms[document_id] = self._load_document(document_id)

        ydoc = self.rooms[document_id]

        # Add client to room
        if document_id not in self.connections:
            self.connections[document_id] = []
        self.connections[document_id].append(websocket)

        try:
            while True:
                data = await websocket.receive_bytes()
                # Sync Y.Doc updates
                await self._sync_update(document_id, data, websocket)
        except WebSocketDisconnect:
            self.connections[document_id].remove(websocket)
            if not self.connections[document_id]:
                self._save_document(document_id, ydoc)
                del self.rooms[document_id]
```

### Task 3.1.2: Implement Collaborative Cursors

**Objective**: Show where other users are editing

**Files**:
- `frontend/src/components/editor/CollaborativeCursors.tsx`
- `frontend/src/lib/yjs-awareness.ts`

**Features**:
- Show cursor position of all users
- Display user name and color
- Fade out after inactivity
- Selection highlighting

**Example**:
```typescript
// frontend/src/components/editor/CollaborativeCursors.tsx
import { Awareness } from 'y-protocols/awareness';
import { useEffect, useState } from 'react';

interface User {
  id: string;
  name: string;
  color: string;
  cursor: { from: number; to: number } | null;
}

export function CollaborativeCursors({ awareness }: { awareness: Awareness }) {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    const updateUsers = () => {
      const states = Array.from(awareness.getStates().entries());
      const activeUsers = states
        .filter(([clientId]) => clientId !== awareness.clientID)
        .map(([clientId, state]) => ({
          id: String(clientId),
          name: state.user?.name || 'Anonymous',
          color: state.user?.color || '#000',
          cursor: state.cursor || null,
        }));
      setUsers(activeUsers);
    };

    awareness.on('change', updateUsers);
    return () => awareness.off('change', updateUsers);
  }, [awareness]);

  return (
    <>
      {users.map(user => user.cursor && (
        <div
          key={user.id}
          className="absolute pointer-events-none"
          style={{
            top: user.cursor.from,
            left: 0,
            borderLeft: `2px solid ${user.color}`,
          }}
        >
          <span
            className="px-1 py-0.5 text-xs text-white rounded"
            style={{ backgroundColor: user.color }}
          >
            {user.name}
          </span>
        </div>
      ))}
    </>
  );
}
```

### Task 3.1.3: Add Presence Awareness

**Objective**: Show who's currently viewing/editing the document

**Files**:
- `frontend/src/components/editor/PresenceAvatars.tsx`

**Features**:
- Avatar list of active users
- Online/offline status
- Join/leave notifications
- User count badge

### Task 3.1.4: Implement Conflict Resolution

**Objective**: Handle edge cases and conflicts gracefully

**Features**:
- Automatic merge of concurrent edits
- Last-write-wins for metadata
- Undo/redo that works with collaboration
- Network partition recovery

**Testing**:
- Test with 10+ concurrent users
- Simulate network issues
- Test rapid concurrent edits
- Verify no data loss

## Phase 3.2: GitHub Publishing

### Overview

Enable users to publish blog posts directly to their GitHub Pages repository.

### Task 3.2.1: GitHub OAuth Integration

**Objective**: Allow users to authenticate with GitHub

**Files**:
- `backend/api/v1/github.py` - GitHub OAuth endpoints
- `backend/services/github_service.py` - GitHub API wrapper
- `frontend/src/components/settings/GitHubConnect.tsx`

**Endpoints**:
- `GET /api/v1/github/oauth/authorize` - Redirect to GitHub OAuth
- `GET /api/v1/github/oauth/callback` - Handle OAuth callback
- `GET /api/v1/github/user` - Get authenticated GitHub user
- `POST /api/v1/github/disconnect` - Revoke GitHub access

**Implementation**:
```python
# backend/api/v1/github.py
from fastapi import APIRouter, Depends
from httpx import AsyncClient
import jwt

router = APIRouter()

@router.get("/oauth/authorize")
async def github_oauth_authorize():
    """Redirect user to GitHub OAuth page"""
    client_id = settings.GITHUB_CLIENT_ID
    redirect_uri = f"{settings.API_URL}/api/v1/github/oauth/callback"
    scope = "repo,user:email"

    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
    )
    return {"url": url}

@router.get("/oauth/callback")
async def github_oauth_callback(code: str, current_user: User = Depends(get_current_user)):
    """Exchange code for access token"""
    async with AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        data = response.json()
        access_token = data["access_token"]

    # Store access token for user
    await save_github_token(current_user.id, access_token)

    return {"success": True}
```

### Task 3.2.2: Repository Selection UI

**Objective**: Let users choose which repository to publish to

**Files**:
- `frontend/src/components/github/RepositorySelector.tsx`
- `backend/api/v1/github.py` (extend)

**Endpoints**:
- `GET /api/v1/github/repositories` - List user's repositories
- `POST /api/v1/github/repositories/{repo_id}/select` - Select repository

**Features**:
- List all user repositories
- Filter by name
- Show repository metadata (stars, forks)
- Create new repository option

### Task 3.2.3: Jekyll Format Conversion

**Objective**: Convert markdown to Jekyll front matter format

**Files**:
- `backend/services/jekyll_service.py`

**Features**:
- Generate Jekyll front matter (title, date, categories, tags)
- Extract metadata from content
- Format images correctly
- Handle code blocks

**Example**:
```python
# backend/services/jekyll_service.py
from datetime import datetime
import yaml

def convert_to_jekyll(
    title: str,
    content: str,
    categories: list[str] = None,
    tags: list[str] = None,
) -> str:
    """Convert markdown content to Jekyll format"""

    # Front matter
    front_matter = {
        "layout": "post",
        "title": title,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S %z"),
        "categories": categories or [],
        "tags": tags or [],
    }

    # Format
    yaml_front_matter = yaml.dump(front_matter, sort_keys=False)
    jekyll_content = f"---\n{yaml_front_matter}---\n\n{content}"

    return jekyll_content
```

### Task 3.2.4: Automated Git Push Workflow

**Objective**: Push blog post to GitHub repository

**Files**:
- `backend/services/github_service.py` (extend)
- `backend/api/v1/blog.py` (add publish endpoint)

**Endpoints**:
- `POST /api/v1/blog/{draft_id}/publish` - Publish to GitHub

**Workflow**:
1. Convert draft to Jekyll format
2. Generate filename (YYYY-MM-DD-title.md)
3. Create commit via GitHub API
4. Push to `_posts/` directory
5. Trigger GitHub Pages rebuild
6. Return published URL

**Implementation**:
```python
async def publish_to_github(
    draft_id: str,
    user_id: str,
    repository: str,
    branch: str = "main"
):
    """Publish blog post to GitHub Pages"""

    # Get draft and GitHub token
    draft = await get_draft(draft_id)
    github_token = await get_github_token(user_id)

    # Convert to Jekyll format
    jekyll_content = convert_to_jekyll(
        title=draft.title,
        content=draft.content,
        categories=draft.categories,
        tags=draft.tags,
    )

    # Generate filename
    filename = f"_posts/{datetime.now().strftime('%Y-%m-%d')}-{slugify(draft.title)}.md"

    # Create or update file via GitHub API
    async with AsyncClient() as client:
        # Check if file exists
        response = await client.get(
            f"https://api.github.com/repos/{repository}/contents/{filename}",
            headers={"Authorization": f"token {github_token}"},
        )

        sha = response.json().get("sha") if response.status_code == 200 else None

        # Create/update file
        await client.put(
            f"https://api.github.com/repos/{repository}/contents/{filename}",
            headers={"Authorization": f"token {github_token}"},
            json={
                "message": f"Publish: {draft.title}",
                "content": base64.b64encode(jekyll_content.encode()).decode(),
                "sha": sha,
                "branch": branch,
            },
        )

    # Build published URL
    username = repository.split("/")[0]
    repo_name = repository.split("/")[1]
    slug = slugify(draft.title)
    published_url = f"https://{username}.github.io/{repo_name}/{slug}/"

    return {"url": published_url, "filename": filename}
```

## Phase 3.3: Additional Features

### Task 3.3.1: Draft Versioning

**Objective**: Track changes and enable rollback

**Features**:
- Auto-save every N seconds
- Version history UI
- Compare versions (diff view)
- Restore previous version

### Task 3.3.2: Commenting System

**Objective**: Allow inline comments and feedback

**Features**:
- Add comments to specific text selections
- Comment threads
- Resolve/unresolve comments
- Notifications

### Task 3.3.3: Export Options

**Objective**: Export to multiple formats

**Features**:
- Markdown (.md)
- PDF
- HTML
- Medium format
- Dev.to format

## Testing Strategy

### Collaboration Tests

```typescript
// Test concurrent editing
test('handles concurrent edits without conflicts', async () => {
  const doc1 = new Y.Doc();
  const doc2 = new Y.Doc();

  const text1 = doc1.getText('content');
  const text2 = doc2.getText('content');

  // User 1 types
  text1.insert(0, 'Hello');

  // User 2 types at same time
  text2.insert(0, 'World');

  // Sync documents
  Y.applyUpdate(doc2, Y.encodeStateAsUpdate(doc1));
  Y.applyUpdate(doc1, Y.encodeStateAsUpdate(doc2));

  // Both should have merged content
  expect(text1.toString()).toBe('HelloWorld');
  expect(text2.toString()).toBe('HelloWorld');
});
```

### GitHub Integration Tests

```python
# Test GitHub publishing
async def test_publish_to_github():
    # Mock GitHub API
    with httpx_mock.mock_api():
        result = await publish_to_github(
            draft_id="123",
            user_id="user1",
            repository="user/blog"
        )
        assert result["url"].startswith("https://")
        assert "_posts/" in result["filename"]
```

## Success Criteria

- ✅ Real-time collaboration with 10+ users
- ✅ No data loss or conflicts
- ✅ Collaborative cursors visible
- ✅ GitHub OAuth working
- ✅ Auto-publish to GitHub Pages
- ✅ Jekyll format correct
- ✅ Version history functional

## Next Steps

After completing Part 3:
1. Update progress in `docs/plans/README.md`
2. Commit: "feat: add real-time collab and GitHub publishing (Part 3)"
3. Push to branch
4. Begin Part 4 (Production Deployment)
