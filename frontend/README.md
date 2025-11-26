# Blog Creator Frontend

Modern Next.js frontend for AI-powered blog content generation.

## Features

- 🔐 **Authentication**: JWT-based auth with login/register
- 📄 **Document Management**: Upload and process documents
- ✍️ **Rich Text Editor**: Tiptap editor with Yjs collaboration
- 🔄 **Real-time Updates**: WebSocket integration
- 🎨 **Modern UI**: Tailwind CSS + responsive design

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Tiptap** - Rich text editor
- **Yjs** - CRDT for real-time collaboration
- **Zustand** - State management
- **Axios** - HTTP client
- **SWR** - Data fetching

## Quick Start

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local with your API URL
nano .env.local
```

### Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                # Next.js 14 app directory
│   │   ├── (auth)/        # Auth routes (login, register)
│   │   ├── (dashboard)/   # Protected dashboard routes
│   │   ├── layout.tsx     # Root layout
│   │   └── page.tsx       # Home page
│   ├── components/        # React components
│   │   ├── ui/           # UI components
│   │   ├── editor/       # Tiptap editor
│   │   └── documents/    # Document components
│   ├── lib/              # Utilities
│   │   └── api.ts        # API client
│   ├── hooks/            # Custom React hooks
│   ├── store/            # Zustand stores
│   │   └── authStore.ts  # Authentication state
│   └── types/            # TypeScript types
│       └── api.ts        # API types
├── public/               # Static assets
├── package.json
├── next.config.js
├── tailwind.config.ts
└── tsconfig.json
```

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME="Blog Creator"
```

## API Integration

The frontend communicates with the FastAPI backend via REST API and WebSocket.

### API Client Usage

```typescript
import { authAPI, documentsAPI, blogAPI } from '@/lib/api';

// Login
const response = await authAPI.login('user@example.com', 'password');

// Upload document
const doc = await documentsAPI.upload(file);

// Generate blog
const draft = await blogAPI.generate({
  document_ids: ['doc-id'],
  title: 'My Blog Post',
  session_id: 'session-id',
});
```

### State Management

```typescript
import { useAuthStore } from '@/store/authStore';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuthStore();

  // Use auth state and actions
}
```

## Development

### Code Style

```bash
# Lint
npm run lint

# Type check
npx tsc --noEmit
```

### Adding Components

1. Create component in `src/components/`
2. Use TypeScript for type safety
3. Style with Tailwind CSS
4. Export from component directory

## Deployment

See `docs/plans/PART_4_PRODUCTION_DEPLOYMENT.md` for deployment instructions.

## License

MIT
