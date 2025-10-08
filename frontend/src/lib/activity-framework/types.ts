/**
 * Activity Framework Types
 *
 * TypeScript interfaces and types for the extensible activity framework.
 */

// Activity Framework Types
export type ActivityState = 'draft' | 'active' | 'paused' | 'completed' | 'cancelled';
export type ActivityPersona = 'admin' | 'viewer' | 'participant';

export type PersonaType = 'admin' | 'viewer' | 'participant';

export interface Activity {
  id: string;
  session_id: number;
  type: string;
  title: string;
  description?: string;
  configuration: Record<string, unknown>;
  activity_metadata: ActivityMetadata;
  state: ActivityState;
  status: string; // Legacy field
  order_index: number;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ActivityMetadata {
  duration_seconds?: number;
  max_responses?: number;
  allow_multiple_responses: boolean;
  show_live_results: boolean;
  activity_type?: string;
  requires_moderation?: boolean;
  [key: string]: unknown;
}

export interface ActivityType {
  id: string;
  name: string;
  description: string;
  version: string;
}

export interface ActivityResponse {
  id: string;
  activity_id: string;
  participant_id: number;
  response_data: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings?: string[];
}

export interface ActivityResults {
  results: Record<string, unknown>;
  last_updated: string;
}

export interface ActivityStatus {
  activity_id: string;
  status: string;
  state: ActivityState;
  response_count: number;
  expires_at?: string;
  activity_metadata: ActivityMetadata;
  valid_transitions: string[];
  results?: Record<string, unknown>;
  last_response_at?: string;
  last_updated: string;
}

// Base component props interfaces
export interface BaseActivityProps {
  activity: Activity;
  configuration: Record<string, unknown>;
  onStateChange: (newState: ActivityState) => void;
}

export interface AdminActivityProps extends BaseActivityProps {
  onConfigUpdate: (config: Record<string, unknown>) => void;
  onSave: () => void;
  validation?: ValidationResult;
  isLoading?: boolean;
}

export interface ViewerActivityProps extends BaseActivityProps {
  responses: ActivityResponse[];
  results?: ActivityResults;
  status?: string;
  liveResults: boolean;
  isLoading?: boolean;
  onRefresh?: () => void;
}

export interface ParticipantActivityProps extends BaseActivityProps {
  onSubmitResponse: (response: unknown) => void;
  canSubmit: boolean;
  hasSubmitted: boolean;
  isSubmitting?: boolean;
  lastResponse?: ActivityResponse;
}

// Activity type definition for registry
export interface ActivityTypeDefinition {
  id: string;
  name: string;
  description: string;
  version: string;
  component: React.ComponentType<any>;
  components?: {
    admin?: React.ComponentType<AdminActivityProps>;
    viewer?: React.ComponentType<ViewerActivityProps>;
    participant?: React.ComponentType<ParticipantActivityProps>;
  };
  schema?: Record<string, unknown>;
}

// Framework configuration
export interface ActivityFrameworkConfig {
  apiBaseUrl?: string;
  pollingInterval?: number;
  enableDevTools?: boolean;
}

// Error types
export interface ActivityError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
