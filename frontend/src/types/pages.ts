/**
 * Next.js page component types
 * Use these for proper typing of page props
 */

/**
 * Generic page props with params (for dynamic routes)
 * In Next.js 15, params are now async Promises
 */
export interface PageProps<Params extends Record<string, string> = Record<string, string>> {
  params: Promise<Params>
  searchParams?: Promise<Record<string, string | string[] | undefined>>
}

/**
 * Specific page props for common routes
 */
export interface EditorPageProps extends PageProps<{ draftId: string }> {}

export interface DocumentPageProps extends PageProps<{ documentId: string }> {}

export interface SessionPageProps extends PageProps<{ sessionId: string }> {}

/**
 * Layout props type
 */
export interface LayoutProps {
  children: React.ReactNode
  params?: Promise<Record<string, string>>
}

/**
 * Error boundary props
 */
export interface ErrorProps {
  error: Error & { digest?: string }
  reset: () => void
}

/**
 * Loading component props (usually empty)
 */
export type LoadingProps = Record<string, never>

/**
 * Metadata generation props (for generateMetadata function)
 */
export interface MetadataProps<Params extends Record<string, string> = Record<string, string>> {
  params: Promise<Params>
  searchParams?: Promise<Record<string, string | string[] | undefined>>
}
