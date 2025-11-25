# TypeScript Usage Audit

**Audit Date:** 2025-11-25  
**TypeScript Version:** 5.3.3

---

## Executive Summary

The codebase has decent TypeScript adoption with proper type definitions for API responses and components. However, there are significant gaps in type coverage, missing Next.js-specific types, implicit any types, and opportunities for improved type safety through advanced TypeScript features.

---

## Findings

### 🟡 HIGH: Missing Next.js-Specific Types

**Severity:** High  
**Location:** All page components and layouts

**Issue:**
Not using Next.js 14 App Router TypeScript types:
- No `Metadata` exports from pages
- No `PageProps` type usage
- No proper typing for `params` and `searchParams`
- Missing route segment config types

**Current Code:**
```typescript
// editor/[draftId]/page.tsx
export default function EditorPage() {
  const params = useParams(); // any type
  const draftId = params.draftId as string; // Manual type assertion
  // ...
}

// No metadata type
// No page props type
```

**Impact:**
- Type safety not enforced
- Autocomplete doesn't work properly
- Runtime errors not caught at compile time
- Missing type hints in IDE

**Recommendation:**

Use proper Next.js types:

```typescript
// app/dashboard/editor/[draftId]/page.tsx
import type { Metadata } from 'next'

// ✅ Type the page props
interface PageProps {
  params: Promise<{ draftId: string }>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}

// ✅ Export metadata with proper type
export const metadata: Metadata = {
  title: 'Editor - Blog Creator',
  description: 'Edit your blog post with AI assistance',
}

// ✅ Or use generateMetadata for dynamic metadata
export async function generateMetadata(
  { params }: PageProps
): Promise<Metadata> {
  const { draftId } = await params
  const draft = await getBlogDraft(draftId)
  
  return {
    title: `${draft.title} - Editor`,
    description: draft.content.substring(0, 160),
    openGraph: {
      title: draft.title,
      description: draft.content.substring(0, 160),
    },
  }
}

// ✅ Type the page component
export default async function EditorPage({ params }: PageProps) {
  const { draftId } = await params
  // Now draftId is properly typed as string
  
  return <EditorContent draftId={draftId} />
}

// For client components that need params
'use client'

export function EditorContent({ draftId }: { draftId: string }) {
  // Use draftId with full type safety
}
```

**Route Segment Config:**
```typescript
// Type route segment configuration
export const dynamic: 'auto' | 'force-dynamic' | 'error' | 'force-static' = 'force-dynamic'
export const dynamicParams: boolean = true
export const revalidate: number | false = false
export const fetchCache: 'auto' | 'default-cache' | 'only-cache' | 'force-cache' | 'force-no-store' | 'default-no-store' | 'only-no-store' = 'auto'
export const runtime: 'nodejs' | 'edge' = 'nodejs'
export const preferredRegion: 'auto' | string | string[] = 'auto'
```

---

### 🟡 HIGH: Implicit Any Types

**Severity:** High  
**Location:** Multiple files

**Issue:**
Many implicit `any` types that bypass type checking:

**Examples:**
```typescript
// lib/api.ts
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ❌ Implicit any in error handler
api.interceptors.response.use(
  (response) => response, // any
  (error: AxiosError) => { // Explicit but error.response is any
    if (error.response?.status === 401) { // error.response is any
      // ...
    }
  }
);

// store/authStore.ts
login: async (email, password) => { // ❌ Parameters implicitly any
  // ...
  } catch (error: any) { // ❌ Explicitly using any
    set({
      error: error.response?.data?.detail || 'Login failed', // any
    });
  }
}

// components
onChange={(e) => setEmail(e.target.value)} // ❌ e is any in some cases
```

**Recommendation:**

Add explicit types everywhere:

```typescript
// lib/api.ts - Properly typed
import type { AxiosError, AxiosResponse } from 'axios'

interface APIError {
  detail: string
  code?: string
}

// Type the response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<APIError>) => {
    if (error.response?.status === 401) {
      // error.response.data.detail is now typed
      console.error(error.response.data.detail)
    }
    return Promise.reject(error)
  }
)

// store/authStore.ts - Properly typed
interface AuthState {
  login: (email: string, password: string) => Promise<void> // ✅ Typed parameters
  // ...
}

export const useAuthStore = create<AuthState>((set) => ({
  login: async (email: string, password: string) => {
    try {
      // ...
    } catch (error) {
      const apiError = error as AxiosError<APIError>
      set({
        error: apiError.response?.data?.detail || 'Login failed',
      })
    }
  }
}))

// Components - Properly typed events
<input
  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
/>

<button
  onClick={(e: React.MouseEvent<HTMLButtonElement>) => handleClick(e)}
/>

<form
  onSubmit={(e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    handleSubmit()
  }}
/>
```

---

### 🟡 HIGH: Missing Generic Types for API Responses

**Severity:** High  
**Location:** `/lib/api.ts`

**Issue:**
API functions don't use generics, returning `any` types:

```typescript
// Current - returns any
export const documentsAPI = {
  list: () => api.get('/api/v1/documents'), // Returns any
  get: (docId: string) => api.get(`/api/v1/documents/${docId}`), // Returns any
}
```

**Recommendation:**

Add proper generic typing:

```typescript
// lib/api-client.ts
import type { AxiosResponse } from 'axios'

// Generic API response wrapper
interface APIResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
}

// Paginated response type
interface PaginatedResponse<T> {
  documents: T[]
  total: number
  page: number
  page_size: number
}

// Documents API with proper typing
export const documentsAPI = {
  // ✅ Returns typed response
  list: () => 
    api.get<PaginatedResponse<Document>>('/api/v1/documents'),
  
  get: (docId: string) => 
    api.get<Document>(`/api/v1/documents/${docId}`),
  
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<Document>('/api/v1/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  
  delete: (docId: string) => 
    api.delete<{ message: string }>(`/api/v1/documents/${docId}`),
  
  search: (query: string, documentIds?: string[], topK: number = 5) => 
    api.post<{ results: SearchResult[] }>('/api/v1/documents/search', {
      query,
      document_ids: documentIds,
      top_k: topK,
    }),
}

// Usage with full type safety
async function loadDocuments() {
  const response = await documentsAPI.list()
  // response.data is typed as PaginatedResponse<Document>
  const documents = response.data.documents // Document[]
  const total = response.data.total // number
}
```

---

### 🟡 HIGH: Weak Component Prop Types

**Severity:** High  
**Location:** Component files

**Issue:**
Component props are typed but could be more specific:

```typescript
// Current - too loose
interface TiptapEditorProps {
  content: string // Could be HTMLString branded type
  onChange: (content: string) => void // No validation
  placeholder?: string
  editable?: boolean
}

// StatCard props - no proper icon typing
interface StatCardProps {
  icon: React.ComponentType<{ className?: string }>; // Too generic
  color: 'blue' | 'green' | 'purple' // Should use const assertion
}
```

**Recommendation:**

Use stricter, more specific types:

```typescript
// Create branded types for strings with specific meanings
type HTMLString = string & { readonly __brand: 'HTMLString' }
type EmailString = string & { readonly __brand: 'EmailString' }
type URLString = string & { readonly __brand: 'URLString' }

// Helper to create branded types
function asHTMLString(str: string): HTMLString {
  return str as HTMLString
}

// Stricter editor props
interface TiptapEditorProps {
  content: HTMLString
  onChange: (content: HTMLString) => void
  placeholder?: string
  editable?: boolean
  className?: string
  'aria-label'?: string // Accessibility
}

// Usage
<TiptapEditor
  content={asHTMLString(draft.content)}
  onChange={(html) => setContent(html)}
/>

// Better icon typing
import type { LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: number
  icon: LucideIcon // ✅ Specific type
  color: 'blue' | 'green' | 'purple'
  loading?: boolean
}

// Even better with const assertion
const STAT_COLORS = ['blue', 'green', 'purple'] as const
type StatColor = typeof STAT_COLORS[number]

interface StatCardProps {
  title: string
  value: number
  icon: LucideIcon
  color: StatColor
  loading?: boolean
  onClick?: () => void
}
```

---

### 🟢 MEDIUM: Missing Discriminated Unions

**Severity:** Medium  
**Location:** Type definitions

**Issue:**
Not using discriminated unions for better type narrowing:

```typescript
// Current - poor type safety
interface APIResponse {
  data?: any
  error?: string
}

// Can have both data and error (invalid state)
```

**Recommendation:**

Use discriminated unions:

```typescript
// ✅ Success and error states are mutually exclusive
type APIResult<T> =
  | { success: true; data: T; error: never }
  | { success: false; error: string; data: never }

// Usage with perfect type narrowing
async function fetchData(): Promise<APIResult<Document[]>> {
  try {
    const response = await documentsAPI.list()
    return { success: true, data: response.data.documents, error: undefined! }
  } catch (error) {
    return { success: false, error: 'Failed to fetch', data: undefined! }
  }
}

// Consuming code
const result = await fetchData()
if (result.success) {
  // TypeScript knows result.data exists and error doesn't
  console.log(result.data) // Document[]
} else {
  // TypeScript knows result.error exists and data doesn't
  console.error(result.error) // string
}

// Another example: Loading states
type LoadingState<T> =
  | { status: 'idle'; data: null; error: null }
  | { status: 'loading'; data: null; error: null }
  | { status: 'success'; data: T; error: null }
  | { status: 'error'; data: null; error: Error }

function Component() {
  const [state, setState] = useState<LoadingState<Document[]>>({
    status: 'idle',
    data: null,
    error: null,
  })
  
  // Perfect type narrowing
  if (state.status === 'loading') {
    return <Spinner />
  }
  
  if (state.status === 'error') {
    return <Error message={state.error.message} />
  }
  
  if (state.status === 'success') {
    return <List data={state.data} /> // state.data is Document[]
  }
  
  return <Idle />
}
```

---

### 🟢 MEDIUM: No Utility Types Usage

**Severity:** Medium  
**Location:** Type definitions

**Issue:**
Not leveraging TypeScript's built-in utility types:

```typescript
// Current - manual type definitions
interface UpdateDocumentData {
  filename?: string
  status?: ProcessingStatus
  chunk_count?: number
}

// Duplicates Document interface partially
```

**Recommendation:**

Use utility types:

```typescript
// Make all properties optional
type PartialDocument = Partial<Document>

// Make all properties required
type RequiredDocument = Required<Document>

// Pick specific properties
type DocumentSummary = Pick<Document, 'id' | 'filename' | 'status'>

// Omit specific properties
type DocumentWithoutDates = Omit<Document, 'created_at' | 'updated_at'>

// Make properties readonly
type ReadonlyDocument = Readonly<Document>

// Practical examples
interface Document {
  id: string
  user_id: string
  filename: string
  file_type: DocumentType
  status: ProcessingStatus
  created_at: string
  updated_at: string
}

// ✅ Update payload - only certain fields can be updated
type UpdateDocumentData = Partial<
  Pick<Document, 'filename' | 'status' | 'chunk_count'>
>

// ✅ Create payload - all fields except auto-generated ones
type CreateDocumentData = Omit<
  Document,
  'id' | 'created_at' | 'updated_at'
>

// ✅ API response - ensure immutability
type DocumentResponse = Readonly<Document>

// ✅ Form data - only user-editable fields
type DocumentFormData = Pick<Document, 'filename' | 'file_type'>

// Advanced: Mapped types
type LoadingStates<T> = {
  [K in keyof T as `${string & K}Loading`]: boolean
}

// Generates: { documentsLoading: boolean, draftsLoading: boolean, ... }
type StatsLoading = LoadingStates<{
  documents: Document[]
  drafts: BlogDraft[]
  sessions: Session[]
}>
```

---

### 🟢 MEDIUM: Missing Const Assertions

**Severity:** Medium  
**Location:** Constants and configuration

**Issue:**
Not using `as const` for literal types:

```typescript
// Current - type is string[]
const ALLOWED_FILE_TYPES = ['pdf', 'audio', 'image']
// Type: string[]

// Current - type is { blue: string, green: string, ... }
const colors = {
  blue: 'bg-blue-50 text-blue-600',
  green: 'bg-green-50 text-green-600',
  purple: 'bg-purple-50 text-purple-600',
}
```

**Recommendation:**

Use const assertions for literal types:

```typescript
// ✅ Type is readonly ['pdf', 'audio', 'image']
const ALLOWED_FILE_TYPES = ['pdf', 'audio', 'image'] as const
type FileType = typeof ALLOWED_FILE_TYPES[number] // 'pdf' | 'audio' | 'image'

// ✅ Full type safety
const colors = {
  blue: 'bg-blue-50 text-blue-600',
  green: 'bg-green-50 text-green-600',
  purple: 'bg-purple-50 text-purple-600',
} as const

type ColorName = keyof typeof colors // 'blue' | 'green' | 'purple'
type ColorClass = typeof colors[ColorName] // The exact string literals

// Usage
function getColorClass(color: ColorName): string {
  return colors[color] // Fully typed
}

// Navigation items
const NAV_ITEMS = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Documents', href: '/dashboard/documents', icon: FileText },
  { name: 'Upload', href: '/dashboard/upload', icon: Upload },
] as const

type NavItem = typeof NAV_ITEMS[number]
type NavPath = NavItem['href'] // '/dashboard' | '/dashboard/documents' | ...
```

---

### 🟢 MEDIUM: No Template Literal Types

**Severity:** Medium  
**Location:** Route paths, API endpoints

**Issue:**
String literals for routes and endpoints not type-safe:

```typescript
// Current - no type safety
router.push('/dashboard/editor/' + draftId) // String concatenation
api.get(`/api/v1/documents/${docId}`) // Template literal but untyped
```

**Recommendation:**

Use template literal types:

```typescript
// Define route structure
type Route =
  | '/'
  | '/login'
  | '/register'
  | '/dashboard'
  | `/dashboard/editor/${string}`
  | '/dashboard/documents'
  | '/dashboard/drafts'
  | '/dashboard/generate'
  | '/dashboard/settings'

// Type-safe navigation
function navigate(route: Route) {
  router.push(route)
}

// ✅ Type-safe
navigate('/dashboard')
navigate(`/dashboard/editor/${draftId}`)

// ❌ Type error
navigate('/invalid-route')

// API Endpoints
type APIEndpoint =
  | '/api/v1/auth/login'
  | '/api/v1/auth/register'
  | '/api/v1/documents'
  | `/api/v1/documents/${string}`
  | '/api/v1/blog'
  | `/api/v1/blog/${string}`

// Type-safe API client
function apiGet<T>(endpoint: APIEndpoint): Promise<T> {
  return fetch(endpoint).then(r => r.json())
}

// Advanced: Build route from params
type BuildRoute<
  T extends string,
  P extends Record<string, string>
> = T extends `${infer Start}:${infer Param}/${infer Rest}`
  ? `${Start}${P[Param]}/${BuildRoute<Rest, P>}`
  : T extends `${infer Start}:${infer Param}`
  ? `${Start}${P[Param]}`
  : T

type EditorRoute = BuildRoute<
  '/dashboard/editor/:draftId',
  { draftId: string }
>
// Result: `/dashboard/editor/${string}`
```

---

### 🟢 MEDIUM: Insufficient Error Types

**Severity:** Medium  
**Location:** Error handling

**Issue:**
Errors typed as `any` or `unknown` without proper handling:

```typescript
catch (error: any) { // ❌
  console.error(error)
  alert('Something went wrong')
}
```

**Recommendation:**

Create specific error types:

```typescript
// lib/errors.ts

// Base error class
export class AppError extends Error {
  constructor(
    message: string,
    public readonly code: ErrorCode,
    public readonly statusCode: number = 500,
    public readonly details?: unknown
  ) {
    super(message)
    this.name = this.constructor.name
    Error.captureStackTrace(this, this.constructor)
  }
}

// Specific error types
export class AuthenticationError extends AppError {
  constructor(message = 'Authentication failed') {
    super(message, 'AUTH_ERROR', 401)
  }
}

export class ValidationError extends AppError {
  constructor(
    message: string,
    public readonly fieldErrors: Record<string, string[]>
  ) {
    super(message, 'VALIDATION_ERROR', 400, fieldErrors)
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, 'NOT_FOUND', 404)
  }
}

export class RateLimitError extends AppError {
  constructor(
    public readonly retryAfter: number
  ) {
    super('Rate limit exceeded', 'RATE_LIMIT', 429, { retryAfter })
  }
}

// Error codes type
const ERROR_CODES = [
  'AUTH_ERROR',
  'VALIDATION_ERROR',
  'NOT_FOUND',
  'RATE_LIMIT',
  'NETWORK_ERROR',
  'SERVER_ERROR',
  'UNKNOWN_ERROR',
] as const

type ErrorCode = typeof ERROR_CODES[number]

// Type guard
export function isAppError(error: unknown): error is AppError {
  return error instanceof AppError
}

// Error handler
export function handleError(error: unknown): AppError {
  if (isAppError(error)) {
    return error
  }
  
  if (error instanceof AxiosError) {
    if (error.response?.status === 401) {
      return new AuthenticationError()
    }
    if (error.response?.status === 404) {
      return new NotFoundError('Resource')
    }
    if (error.response?.status === 429) {
      const retryAfter = Number(error.response.headers['retry-after']) || 60
      return new RateLimitError(retryAfter)
    }
  }
  
  return new AppError(
    'An unexpected error occurred',
    'UNKNOWN_ERROR',
    500,
    error
  )
}

// Usage
try {
  await documentsAPI.delete(docId)
} catch (error) {
  const appError = handleError(error)
  
  if (appError instanceof NotFoundError) {
    toast.error('Document not found')
  } else if (appError instanceof RateLimitError) {
    toast.error(`Too many requests. Try again in ${appError.retryAfter}s`)
  } else {
    toast.error(appError.message)
  }
  
  // Log for monitoring
  logger.error('Failed to delete document', {
    code: appError.code,
    message: appError.message,
    details: appError.details,
  })
}
```

---

### 🔵 LOW: Missing JSDoc Types

**Severity:** Low  
**Location:** Complex functions

**Issue:**
No JSDoc comments with type information for complex functions.

**Recommendation:**

```typescript
/**
 * Fetches and filters documents based on status
 * @param status - The processing status to filter by
 * @param limit - Maximum number of documents to return
 * @returns Promise resolving to filtered documents
 * @throws {NotFoundError} If no documents match the criteria
 * @example
 * ```ts
 * const docs = await getDocumentsByStatus('completed', 10)
 * ```
 */
export async function getDocumentsByStatus(
  status: ProcessingStatus,
  limit: number = 10
): Promise<Document[]> {
  const response = await documentsAPI.list()
  return response.data.documents
    .filter(doc => doc.status === status)
    .slice(0, limit)
}
```

---

## Type Coverage Analysis

### Current Estimated Coverage
```
Explicit Types:     60%
Implicit Any:       25%
Type Assertions:    10%
Unknown/Any:        5%
```

### Target Coverage
```
Explicit Types:     >95%
Implicit Any:       <1%
Type Assertions:    <3%
Unknown (proper):   <2%
```

---

## TypeScript Configuration Improvements

**Current `tsconfig.json` is good but can be enhanced:**

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    
    // ✅ Add these for better type safety
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,
    
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## Implementation Priority

### Week 1: Critical Type Safety
1. ✅ Add Next.js-specific types to all pages
2. ✅ Remove all implicit any types
3. ✅ Add generic types to API functions
4. ✅ Create error type hierarchy

### Week 2: Advanced Types
5. ✅ Implement discriminated unions
6. ✅ Add utility types usage
7. ✅ Use const assertions
8. ✅ Add template literal types

### Week 3: Polish & Documentation
9. ✅ Add JSDoc comments
10. ✅ Export all prop types
11. ✅ Enable stricter TypeScript config
12. ✅ Fix all type errors

---

## Tools & Resources

### Type Checking Tools
```bash
# Check for unused exports
npx ts-prune

# Check for type coverage
npx type-coverage

# Generate type documentation
npx typedoc
```

### Recommended Libraries
```bash
npm install zod # Runtime type validation
npm install type-fest # Additional utility types
npm install ts-pattern # Pattern matching
```

### Resources
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)
- [Next.js TypeScript](https://nextjs.org/docs/app/building-your-application/configuring/typescript)
- [Total TypeScript](https://www.totaltypescript.com/)
