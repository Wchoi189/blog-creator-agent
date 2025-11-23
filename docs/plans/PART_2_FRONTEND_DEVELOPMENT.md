# Part 2: Frontend Development (Next.js)

## Status: ⏸️ Pending (0%)

**Goal**: Build a modern Next.js frontend with rich text editing and real-time collaboration capabilities.

## Architecture Overview

```
frontend/
├── src/
│   ├── app/                    # Next.js 14 app directory
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   ├── (auth)/            # Auth group
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/       # Protected routes
│   │   │   ├── layout.tsx    # Dashboard layout
│   │   │   ├── documents/    # Document management
│   │   │   ├── editor/       # Blog editor
│   │   │   └── settings/     # User settings
│   │   └── api/              # API routes (if needed)
│   ├── components/           # React components
│   │   ├── ui/              # Shadcn UI components
│   │   ├── editor/          # Tiptap editor components
│   │   ├── layout/          # Layout components
│   │   └── documents/       # Document components
│   ├── lib/                 # Utility libraries
│   │   ├── api.ts          # API client
│   │   ├── auth.ts         # Auth utilities
│   │   ├── websocket.ts    # WebSocket client
│   │   └── yjs.ts          # Yjs setup
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useEditor.ts
│   │   └── useWebSocket.ts
│   ├── store/              # State management (Zustand)
│   │   ├── authStore.ts
│   │   ├── editorStore.ts
│   │   └── documentStore.ts
│   └── types/              # TypeScript types
│       ├── api.ts
│       ├── editor.ts
│       └── document.ts
├── public/                 # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Phase 2.1: Next.js Foundation

### Task 2.1.1: Initialize Next.js Project

**Objective**: Setup Next.js 14 with TypeScript and Tailwind

**Actions**:
```bash
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir
```

**Configuration**:
- Enable `src/` directory
- Configure Tailwind CSS
- Setup path aliases (@/)
- Configure ESLint & Prettier

**Dependencies**:
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.3",
    "@tiptap/react": "2.1.13",
    "@tiptap/starter-kit": "2.1.13",
    "yjs": "13.6.10",
    "y-websocket": "1.5.0",
    "axios": "1.6.2",
    "swr": "2.2.4",
    "zustand": "4.4.7",
    "tailwindcss": "3.4.0",
    "@radix-ui/react-*": "latest",
    "class-variance-authority": "0.7.0",
    "clsx": "2.0.0",
    "tailwind-merge": "2.2.0"
  },
  "devDependencies": {
    "@types/node": "20.10.6",
    "@types/react": "18.2.46",
    "@types/react-dom": "18.2.18",
    "eslint": "8.56.0",
    "eslint-config-next": "14.0.4",
    "prettier": "3.1.1"
  }
}
```

### Task 2.1.2: Setup UI Component Library

**Objective**: Install and configure Shadcn UI

**Actions**:
```bash
npx shadcn-ui@latest init
```

**Components to add**:
- Button, Input, Textarea
- Card, Dialog, DropdownMenu
- Tabs, Accordion, Select
- Toast, Progress, Skeleton

### Task 2.1.3: Create API Client

**Objective**: Build type-safe API client for backend communication

**Files**:
- `src/lib/api.ts` - Axios instance with interceptors
- `src/types/api.ts` - TypeScript types matching backend models

**Features**:
- Automatic JWT token handling
- Request/response interceptors
- Error handling
- TypeScript types for all endpoints

**Example**:
```typescript
// src/lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
});

// Request interceptor for JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/api/v1/auth/login', { email, password }),
  register: (data: RegisterData) =>
    api.post('/api/v1/auth/register', data),
  // ... more methods
};

export const documentsAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/v1/documents/upload', formData);
  },
  list: () => api.get('/api/v1/documents'),
  // ... more methods
};
```

### Task 2.1.4: Core Layout & Navigation

**Objective**: Create responsive layout with navigation

**Files**:
- `src/app/layout.tsx` - Root layout
- `src/app/(dashboard)/layout.tsx` - Dashboard layout
- `src/components/layout/Navbar.tsx` - Navigation bar
- `src/components/layout/Sidebar.tsx` - Sidebar navigation

**Features**:
- Responsive design (mobile, tablet, desktop)
- User menu with logout
- Active route highlighting
- Breadcrumbs

### Task 2.1.5: Authentication Flow

**Objective**: Implement login/register pages and protected routes

**Files**:
- `src/app/(auth)/login/page.tsx`
- `src/app/(auth)/register/page.tsx`
- `src/hooks/useAuth.ts`
- `src/store/authStore.ts`

**Features**:
- Login form with validation
- Registration form
- Protected route middleware
- Persistent authentication (localStorage)
- Auto-redirect after login

## Phase 2.2: Document Editor

### Task 2.2.1: Setup Tiptap Editor

**Objective**: Integrate Tiptap rich text editor

**Files**:
- `src/components/editor/TiptapEditor.tsx`
- `src/hooks/useEditor.ts`

**Extensions**:
- StarterKit (basic formatting)
- Placeholder
- CharacterCount
- Link
- Image
- CodeBlock
- Table

**Features**:
- Toolbar with formatting options
- Markdown shortcuts
- Character count
- Word count
- Auto-save

**Example**:
```typescript
// src/components/editor/TiptapEditor.tsx
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';

export function TiptapEditor({ content, onChange }) {
  const editor = useEditor({
    extensions: [StarterKit],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });

  return (
    <div className="border rounded-lg">
      <EditorToolbar editor={editor} />
      <EditorContent editor={editor} className="prose p-4" />
    </div>
  );
}
```

### Task 2.2.2: Add Yjs for Collaboration

**Objective**: Enable real-time collaborative editing

**Files**:
- `src/lib/yjs.ts` - Yjs provider setup
- `src/components/editor/CollaborativeEditor.tsx`

**Dependencies**:
- `yjs` - CRDT library
- `y-websocket` - WebSocket provider
- `@tiptap/extension-collaboration` - Tiptap Yjs integration

**Features**:
- Real-time sync across clients
- Conflict-free editing
- User cursors
- Presence awareness

**Example**:
```typescript
import { WebsocketProvider } from 'y-websocket';
import * as Y from 'yjs';
import Collaboration from '@tiptap/extension-collaboration';

const ydoc = new Y.Doc();
const provider = new WebsocketProvider(
  'ws://localhost:8000/ws',
  'document-id',
  ydoc
);

const editor = useEditor({
  extensions: [
    StarterKit,
    Collaboration.configure({
      document: ydoc,
    }),
  ],
});
```

### Task 2.2.3: Document Management UI

**Objective**: Build document listing and management interface

**Files**:
- `src/app/(dashboard)/documents/page.tsx`
- `src/components/documents/DocumentList.tsx`
- `src/components/documents/DocumentCard.tsx`
- `src/components/documents/UploadDialog.tsx`

**Features**:
- List all documents with thumbnails
- Upload new documents (drag & drop)
- Delete documents
- Search and filter
- Document metadata display

### Task 2.2.4: Real-time Updates via WebSocket

**Objective**: Implement WebSocket connection for live updates

**Files**:
- `src/lib/websocket.ts`
- `src/hooks/useWebSocket.ts`

**Features**:
- Automatic reconnection
- Heartbeat/ping-pong
- Event handling (document processed, draft updated)
- Connection status indicator

**Example**:
```typescript
// src/hooks/useWebSocket.ts
export function useWebSocket(sessionId: string) {
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

    ws.onopen = () => setStatus('connected');
    ws.onclose = () => setStatus('disconnected');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Handle different message types
    };

    return () => ws.close();
  }, [sessionId]);

  return { status };
}
```

## Phase 2.3: Blog Creation Flow

### Task 2.3.1: File Upload Interface

**Objective**: Create intuitive file upload experience

**Files**:
- `src/components/documents/FileUpload.tsx`

**Features**:
- Drag and drop zone
- Multiple file support
- File type validation
- Upload progress bar
- Preview thumbnails

### Task 2.3.2: Document Processing UI

**Objective**: Show processing status and results

**Files**:
- `src/components/documents/ProcessingStatus.tsx`

**Features**:
- Processing progress indicator
- Chunk count and metadata display
- Error handling
- Retry failed processing

### Task 2.3.3: Draft Generation & Editing

**Objective**: Generate and edit blog drafts

**Files**:
- `src/app/(dashboard)/editor/[draftId]/page.tsx`
- `src/components/editor/DraftEditor.tsx`

**Features**:
- Generate draft from documents
- Stream LLM responses
- Edit draft in Tiptap editor
- Refine with AI (send feedback)
- Version history
- Undo/redo

### Task 2.3.4: Preview & Export

**Objective**: Preview and export blog posts

**Files**:
- `src/components/editor/PreviewPane.tsx`
- `src/components/editor/ExportDialog.tsx`

**Features**:
- Live markdown preview
- Export to .md file
- Copy to clipboard
- Publish to GitHub (Part 3)

## State Management

Using **Zustand** for global state:

```typescript
// src/store/editorStore.ts
import create from 'zustand';

interface EditorStore {
  content: string;
  isDirty: boolean;
  setContent: (content: string) => void;
  save: () => Promise<void>;
}

export const useEditorStore = create<EditorStore>((set, get) => ({
  content: '',
  isDirty: false,
  setContent: (content) => set({ content, isDirty: true }),
  save: async () => {
    const { content } = get();
    await documentsAPI.saveDraft(content);
    set({ isDirty: false });
  },
}));
```

## Styling

### Tailwind Configuration

```typescript
// tailwind.config.ts
export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#6366f1',
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '65ch',
            // ... custom prose styles
          },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
```

## Testing

### Unit Tests (Jest + React Testing Library)

```typescript
// src/components/editor/__tests__/TiptapEditor.test.tsx
import { render, screen } from '@testing-library/react';
import { TiptapEditor } from '../TiptapEditor';

test('renders editor with content', () => {
  render(<TiptapEditor content="Hello" onChange={() => {}} />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});
```

### E2E Tests (Playwright)

```typescript
// tests/e2e/editor.spec.ts
import { test, expect } from '@playwright/test';

test('can create and edit blog draft', async ({ page }) => {
  await page.goto('/editor/new');
  await page.fill('[data-testid="editor"]', 'My blog post');
  await page.click('[data-testid="save"]');
  await expect(page.locator('.toast')).toContainText('Saved');
});
```

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME="Blog Creator"
```

## Success Criteria

- ✅ Next.js app running on port 3000
- ✅ Authentication flow working
- ✅ Document upload and processing functional
- ✅ Tiptap editor integrated
- ✅ Real-time updates via WebSocket
- ✅ Responsive design (mobile + desktop)
- ✅ All components tested
- ✅ Type-safe API client

## Next Steps

After completing Part 2:
1. Update progress in `docs/plans/README.md`
2. Commit changes: "feat: complete Next.js frontend (Part 2)"
3. Push to branch
4. Begin Part 3 (Advanced Features)
