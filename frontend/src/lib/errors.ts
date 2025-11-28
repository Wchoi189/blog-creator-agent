/**
 * Error handling utilities for the application
 */

/**
 * Custom error types for better error handling
 */
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class AuthenticationError extends Error {
  constructor(message: string = 'Authentication required') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class ValidationError extends Error {
  constructor(
    message: string,
    public field?: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class NetworkError extends Error {
  constructor(message: string = 'Network request failed') {
    super(message);
    this.name = 'NetworkError';
  }
}

/**
 * Type guard to check if an error is an APIError
 */
export function isAPIError(error: unknown): error is APIError {
  return error instanceof APIError;
}

/**
 * Type guard to check if an error is an axios-like error
 */
export function isAxiosError(error: unknown): error is {
  response?: { status?: number; data?: { detail?: string } };
  message?: string;
} {
  return (
    typeof error === 'object' &&
    error !== null &&
    ('response' in error || 'message' in error)
  );
}

/**
 * Extract a user-friendly error message from any error type
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (isAxiosError(error)) {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.message) {
      return error.message;
    }
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'An unexpected error occurred';
}

/**
 * Get HTTP status code from error
 */
export function getErrorStatusCode(error: unknown): number | undefined {
  if (error instanceof APIError) {
    return error.statusCode;
  }
  
  if (isAxiosError(error)) {
    return error.response?.status;
  }
  
  return undefined;
}

/**
 * Check if error is an authentication error (401)
 */
export function isAuthError(error: unknown): boolean {
  const statusCode = getErrorStatusCode(error);
  return statusCode === 401;
}

/**
 * Check if error is a not found error (404)
 */
export function isNotFoundError(error: unknown): boolean {
  const statusCode = getErrorStatusCode(error);
  return statusCode === 404;
}

/**
 * Check if error is a server error (5xx)
 */
export function isServerError(error: unknown): boolean {
  const statusCode = getErrorStatusCode(error);
  return statusCode !== undefined && statusCode >= 500;
}

/**
 * Safe wrapper for async functions with error handling
 */
export async function tryCatch<T>(
  fn: () => Promise<T>,
  options?: {
    onError?: (error: unknown) => void;
    fallback?: T;
  }
): Promise<{ data: T | undefined; error: unknown | undefined }> {
  try {
    const data = await fn();
    return { data, error: undefined };
  } catch (error) {
    options?.onError?.(error);
    return { data: options?.fallback, error };
  }
}

/**
 * Format error for logging (includes stack trace in development)
 */
export function formatErrorForLogging(error: unknown): string {
  if (error instanceof Error) {
    if (process.env.NODE_ENV === 'development') {
      return `${error.name}: ${error.message}\n${error.stack}`;
    }
    return `${error.name}: ${error.message}`;
  }
  return String(error);
}
