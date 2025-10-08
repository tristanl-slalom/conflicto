import { env } from '../env';

/**
 * Custom fetcher for Orval-generated API client that uses environment-configured base URL
 * instead of hardcoded localhost URLs.
 *
 * This mutator replaces the default fetch behavior to:
 * - Use VITE_API_BASE_URL from environment variables
 * - Handle relative and absolute URLs correctly
 * - Provide consistent error handling
 * - Maintain compatibility with TanStack Query
 */
export const customFetcher = <T>(
  url: string,
  options?: RequestInit
): Promise<T> => {
  const baseUrl = env.VITE_API_BASE_URL;

  // If URL is already absolute (starts with http/https), use it as-is
  // Otherwise, prepend the base URL
  const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;

  return fetch(fullUrl, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  }).then(async (response) => {
    if (!response.ok) {
      const errorMessage = `HTTP ${response.status}: ${response.statusText}`;

      // Try to parse error response body for more context
      try {
        const errorBody = await response.text();
        throw new Error(errorBody ? `${errorMessage} - ${errorBody}` : errorMessage);
      } catch {
        throw new Error(errorMessage);
      }
    }

    // Handle empty responses (e.g., 204 No Content)
    if (response.status === 204 || response.headers.get('content-length') === '0') {
      return {} as T;
    }

    return response.json();
  });
};
