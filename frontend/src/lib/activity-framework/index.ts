/**
 * Activity Framework
 *
 * Extensible activity framework for the Caja live event platform.
 */

// Core types and interfaces
export * from './types';

// Base component classes
export * from './BaseActivityComponent';

// Registry system
export * from './ActivityRegistry';

// Activity renderer
export { default as ActivityRenderer } from './ActivityRenderer';

// Re-export commonly used types for convenience
export type {
  Activity,
  ActivityType,
  ActivityState,
  ActivityPersona,
  BaseActivityProps,
  AdminActivityProps,
  ViewerActivityProps,
  ParticipantActivityProps,
  ActivityTypeDefinition,
  ValidationResult,
} from './types';

// Re-export registry instance and functions
export {
  activityRegistry,
  registerActivity,
  getActivity,
  hasActivity,
  getAllActivities,
  createActivityComponent,
} from './ActivityRegistry';
