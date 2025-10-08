import { useQuery } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { getSessionStatusApiV1SessionsSessionIdStatusGet, SessionStatus } from '../api/generated';

interface UseRealTimeUpdatesOptions {
  sessionId?: number;
  enabled?: boolean;
  onStatusChange?: (status: SessionStatus) => void;
  onParticipantCountChange?: (count: number) => void;
  pollingInterval?: number;
}

interface RealTimeData {
  status: SessionStatus;
  participantCount: number;
  currentActivityId?: string | null;
  lastUpdated: string;
}

export function useRealTimeUpdates({
  sessionId,
  enabled = true,
  onStatusChange,
  onParticipantCountChange,
  pollingInterval = 3000, // 3 seconds default
}: UseRealTimeUpdatesOptions) {
  const previousData = useRef<RealTimeData | null>(null);

  const queryResult = useQuery({
    queryKey: ['session-status', sessionId],
    queryFn: async () => {
      if (!sessionId) throw new Error('No session ID provided');

      const response = await getSessionStatusApiV1SessionsSessionIdStatusGet(sessionId);

      if ('data' in response && response.data && 'status' in response.data) {
        const sessionData = response.data;
        return {
          status: sessionData.status,
          participantCount: sessionData.participant_count,
          currentActivityId: sessionData.current_activity_id ?? null,
          lastUpdated: sessionData.last_updated,
        };
      }

      throw new Error('Invalid response format');
    },
    enabled: enabled && !!sessionId,
    refetchInterval: pollingInterval,
    refetchIntervalInBackground: true,
  });

  const data = queryResult.data as RealTimeData | undefined;

  // Call callbacks when data changes
  useEffect(() => {
    if (!data || !previousData.current) {
      if (data) {
        previousData.current = data;
      }
      return;
    }

    const prev = previousData.current;

    // Check for status changes
    if (data.status !== prev.status && onStatusChange) {
      onStatusChange(data.status);
    }

    // Check for participant count changes
    if (data.participantCount !== prev.participantCount && onParticipantCountChange) {
      onParticipantCountChange(data.participantCount);
    }

    previousData.current = data;
  }, [data, onStatusChange, onParticipantCountChange]);

  return {
    data,
    error: queryResult.error,
    isLoading: queryResult.isLoading,
    refetch: queryResult.refetch,
    // Convenience properties
    status: data?.status,
    participantCount: data?.participantCount ?? 0,
    currentActivityId: data?.currentActivityId,
    lastUpdated: data?.lastUpdated,
  };
}
