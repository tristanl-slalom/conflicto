import type { SessionDetail, SessionResponse } from '../api/generated';

/**
 * Form state for session creation
 */
export interface SessionFormState {
  isSubmitting: boolean;
  lastCreatedSession?: SessionDetail;
  error?: string;
  success?: string;
}

/**
 * Session creation form data (local form state)
 */
export interface SessionCreateFormData {
  title: string;
  description?: string;
}

/**
 * Session list state
 */
export interface SessionListState {
  sessions: SessionResponse[];
  isLoading: boolean;
  error?: string;
  total: number;
}

/**
 * Admin dashboard state
 */
export interface AdminDashboardState {
  currentSession?: SessionDetail;
  recentSessions: SessionResponse[];
  isCreatingSession: boolean;
  sessionCreationError?: string;
  sessionCreationSuccess?: string;
}

/**
 * Session quick action types
 */
export type SessionAction = 
  | 'view'
  | 'edit'
  | 'start'
  | 'stop'
  | 'delete'
  | 'duplicate';

/**
 * Session action handler
 */
export interface SessionActionHandler {
  action: SessionAction;
  sessionId: number;
  data?: unknown;
}

/**
 * Component props for session components
 */
export interface SessionCreateFormProps {
  onSuccess?: (session: SessionDetail) => void;
  onError?: (error: string) => void;
  className?: string;
}

export interface SessionListProps {
  onSessionSelect?: (session: SessionResponse) => void;
  showActions?: boolean;
  maxItems?: number;
  className?: string;
}

export interface SessionStatusCardProps {
  session?: SessionDetail;
  isLoading?: boolean;
  onRefresh?: () => void;
  className?: string;
}