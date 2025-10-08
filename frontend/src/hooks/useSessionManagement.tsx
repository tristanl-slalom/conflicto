import { useState, useCallback } from 'react';
import { 
  useCreateSessionApiV1SessionsPost,
  useListSessionsApiV1SessionsGet,
  useGetSessionApiV1SessionsSessionIdGet,
  type SessionCreate
} from '../api/generated';
import type { SessionCreateFormData, SessionFormState } from '../types/admin';

/**
 * Custom hook for session management operations
 */
export const useSessionManagement = () => {
  const [formState, setFormState] = useState<SessionFormState>({
    isSubmitting: false,
  });

  // API hooks
  const createSessionMutation = useCreateSessionApiV1SessionsPost();
  const { 
    data: sessionsData, 
    refetch: refetchSessions,
    isLoading: isLoadingSessions,
    error: sessionsError 
  } = useListSessionsApiV1SessionsGet();

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

      // Refresh the sessions list
      await refetchSessions();

      setFormState({
        isSubmitting: false,
        lastCreatedSession: response.data,
        success: 'Session created successfully!',
      });

      return response.data;
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
          enabled: !!sessionId 
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
    sessions: sessionsData?.data?.sessions || [],
    totalSessions: sessionsData?.data?.total || 0,
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