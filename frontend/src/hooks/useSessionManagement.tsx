import { useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import {
  useCreateSessionApiV1SessionsPost,
  useListSessionsApiV1SessionsGet,
  useGetSessionApiV1SessionsSessionIdGet,
  getListSessionsApiV1SessionsGetQueryKey,
  type SessionCreate,
  type SessionDetail
} from '../api/generated';
import type { SessionCreateFormData, SessionFormState } from '../types/admin';

/**
 * Custom hook for session management operations
 */
export const useSessionManagement = () => {
  const [formState, setFormState] = useState<SessionFormState>({
    isSubmitting: false,
  });

  // Query client for cache invalidation
  const queryClient = useQueryClient();

  // API hooks
  const createSessionMutation = useCreateSessionApiV1SessionsPost();
  const {
    data: sessionsData,
    refetch: refetchSessions,
    isLoading: isLoadingSessions,
    error: sessionsError
  } = useListSessionsApiV1SessionsGet(
    undefined, // No params needed
    {
      query: {
        retry: 1, // Only retry once on failure
        retryDelay: 2000, // Wait 2 seconds before retry
        refetchOnWindowFocus: false, // Don't refetch when window gains focus
        staleTime: 30000, // Consider data stale after 30 seconds
      }
    }
  );

  /**
   * Create a new session
   */
  const createSession = useCallback(async (formData: SessionCreateFormData) => {
    setFormState(prev => ({ ...prev, isSubmitting: true, error: undefined, success: undefined }));

    try {
      const sessionCreateData: SessionCreate = {
        title: formData.title,
        description: formData.description || undefined,
      };

      console.log('🚀 Creating session with data:', sessionCreateData);
      console.log('🔗 API call about to be made...');

      const response = await createSessionMutation.mutateAsync({
        data: sessionCreateData
      });

      console.log('✅ Session created successfully:', response.data);

      // Invalidate sessions cache to trigger refetch across all components
      await queryClient.invalidateQueries({ queryKey: getListSessionsApiV1SessionsGetQueryKey() });

      // Convert SessionResponse to SessionDetail (they're compatible types)
      const sessionDetail = response.data as SessionDetail;

      setFormState({
        isSubmitting: false,
        lastCreatedSession: sessionDetail,
        success: 'Session created successfully!',
      });

      return sessionDetail;
    } catch (error) {
      console.error('❌ Session creation failed:', error);
      console.error('Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        response: (error as any)?.response?.data,
        status: (error as any)?.response?.status,
        url: (error as any)?.config?.url,
      });

      const errorMessage = error instanceof Error
        ? error.message
        : 'Failed to create session. Please try again.';

      setFormState({
        isSubmitting: false,
        error: errorMessage,
      });

      throw error;
    }
  }, [createSessionMutation, refetchSessions]);

  /**
   * Clear form state
   */
  const clearFormState = useCallback(() => {
    setFormState({
      isSubmitting: false,
    });
  }, []);

  /**
   * Get session by ID
   */
  const useSessionById = (sessionId: number | undefined) => {
    return useGetSessionApiV1SessionsSessionIdGet(
      sessionId!,
      {
        query: {
          enabled: !!sessionId,
          retry: 1, // Only retry once on failure
          retryDelay: 2000, // Wait 2 seconds before retry
          refetchOnWindowFocus: false, // Don't refetch when window gains focus
          staleTime: 30000, // Consider data stale after 30 seconds
        }
      }
    );
  };

  return {
    // Session creation
    createSession,
    formState,
    clearFormState,

    // Session list
    sessions: (sessionsData?.status === 200 && 'sessions' in sessionsData.data)
      ? sessionsData.data.sessions
      : [],
    totalSessions: (sessionsData?.status === 200 && 'total' in sessionsData.data)
      ? sessionsData.data.total
      : 0,
    isLoadingSessions,
    sessionsError,
    refetchSessions,

    // Utilities
    useSessionById,

    // Computed states
    isCreating: formState.isSubmitting,
    creationError: formState.error,
    creationSuccess: formState.success,
    lastCreatedSession: formState.lastCreatedSession,
  };
};
