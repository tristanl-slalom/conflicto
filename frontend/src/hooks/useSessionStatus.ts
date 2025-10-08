import { useEffect, useState } from 'react';
import { useGetSessionApiV1SessionsSessionIdGet } from '../api/generated';

export interface SessionStatusData {
  sessionId: number;
  status: 'draft' | 'active' | 'completed' | 'unknown';
  title?: string;
  description?: string;
  participantCount: number;
  isLoading: boolean;
  error?: string;
}

export interface UseSessionStatusOptions {
  pollingInterval?: number;
  enabled?: boolean;
}

/**
 * Hook for managing session status detection and polling
 * Uses existing session API to get status information
 */
export const useSessionStatus = (
  sessionId: number,
  options: UseSessionStatusOptions = {}
): SessionStatusData => {
  const { 
    pollingInterval = 5000, // Poll every 5 seconds by default
    enabled = true 
  } = options;

  const [previousStatus, setPreviousStatus] = useState<string | null>(null);

  // Use existing session API with polling
  const { 
    data: sessionData, 
    isLoading, 
    error 
  } = useGetSessionApiV1SessionsSessionIdGet(
    sessionId,
    {
      query: {
        enabled,
        refetchInterval: pollingInterval,
        refetchIntervalInBackground: true,
        staleTime: 1000, // Consider data stale after 1 second
      }
    }
  );

  const session = sessionData?.status === 200 ? sessionData.data : null;
  const currentStatus = session?.status || 'unknown';

  // Track status changes for potential callbacks/effects
  useEffect(() => {
    if (currentStatus !== 'unknown' && currentStatus !== previousStatus) {
      if (previousStatus !== null) {
        console.log(`Session ${sessionId} status changed: ${previousStatus} → ${currentStatus}`);
      }
      setPreviousStatus(currentStatus);
    }
  }, [currentStatus, previousStatus, sessionId]);

  // Determine error message
  let errorMessage: string | undefined;
  if (error) {
    if ('error' in error && typeof error.error === 'string') {
      errorMessage = error.error;
    } else {
      errorMessage = 'Failed to load session status';
    }
  }

  return {
    sessionId,
    status: currentStatus as 'draft' | 'active' | 'completed' | 'unknown',
    title: session?.title,
    description: session?.description || undefined,
    participantCount: session?.participant_count || 0,
    isLoading,
    error: errorMessage,
  };
};

/**
 * Hook specifically for detecting when a session transitions to active
 * Useful for redirecting from pre-lobby to active session
 */
export const useSessionTransition = (
  sessionId: number,
  onStatusChange?: (newStatus: string, previousStatus: string | null) => void
) => {
  const [previousStatus, setPreviousStatus] = useState<string | null>(null);
  const sessionStatus = useSessionStatus(sessionId);

  useEffect(() => {
    if (sessionStatus.status !== 'unknown' && sessionStatus.status !== previousStatus) {
      if (previousStatus !== null && onStatusChange) {
        onStatusChange(sessionStatus.status, previousStatus);
      }
      setPreviousStatus(sessionStatus.status);
    }
  }, [sessionStatus.status, previousStatus, onStatusChange]);

  return {
    ...sessionStatus,
    hasTransitioned: previousStatus !== null && sessionStatus.status !== previousStatus,
    previousStatus,
  };
};