/**
 * Base Activity Component
 *
 * Abstract base class that all activity components must extend.
 */

import React from 'react';
import {
  AdminActivityProps,
  ViewerActivityProps,
  ParticipantActivityProps,
  PersonaType
} from './types';

export abstract class BaseActivityComponent<TConfig = Record<string, unknown>> {
  /**
   * Render the admin interface for this activity type.
   * This interface allows admins to configure the activity.
   */
  abstract renderAdmin(props: AdminActivityProps): React.ReactElement;

  /**
   * Render the viewer interface for this activity type.
   * This interface displays live results on large screens/projectors.
   */
  abstract renderViewer(props: ViewerActivityProps): React.ReactElement;

  /**
   * Render the participant interface for this activity type.
   * This interface allows participants to interact with the activity on mobile devices.
   */
  abstract renderParticipant(props: ParticipantActivityProps): React.ReactElement;

  /**
   * Validate configuration for this activity type.
   * Override to provide custom validation logic.
   */
  validateConfiguration(_config: TConfig): { valid: boolean; errors: string[] } {
    return { valid: true, errors: [] };
  }

  /**
   * Get default configuration for this activity type.
   * Override to provide activity-specific defaults.
   */
  getDefaultConfiguration(): TConfig {
    return {} as TConfig;
  }

  /**
   * Get the JSON schema for this activity type's configuration.
   * Override to provide validation schema.
   */
  getSchema(): Record<string, unknown> {
    return {};
  }

  /**
   * Process activity results for display.
   * Override to provide custom result processing.
   */
  processResults(results: Record<string, unknown>): Record<string, unknown> {
    return results;
  }

  /**
   * Handle activity state changes.
   * Override to perform actions when activity state changes.
   */
  onStateChange(
    _oldState: string,
    _newState: string,
    _activity: any
  ): void {
    // Default implementation does nothing
  }

  /**
   * Check if the activity supports a specific persona.
   * All activities must support all personas by default.
   */
  supportsPersona(_persona: PersonaType): boolean {
    return true; // All activities must support all personas
  }

  /**
   * Get display name for this activity type.
   * Override to provide custom display name.
   */
  getDisplayName(): string {
    return this.constructor.name.replace('Activity', '');
  }
}

/**
 * Activity Component Props for rendering any persona
 */
export interface ActivityComponentProps {
  activity: any;
  persona: PersonaType;
  responses?: any[];
  results?: any;
  onConfigUpdate?: (config: Record<string, unknown>) => void;
  onSubmitResponse?: (response: unknown) => void;
  onSave?: () => void;
  onStateChange?: (newState: string) => void;
  validation?: { valid: boolean; errors: string[] };
  isLoading?: boolean;
  isSubmitting?: boolean;
  canSubmit?: boolean;
  hasSubmitted?: boolean;
  lastResponse?: any;
  liveResults?: boolean;
}

/**
 * Default Activity Component Wrapper
 *
 * Wraps activity components and handles persona routing.
 */
export class ActivityComponentWrapper extends React.Component<ActivityComponentProps> {
  render() {
    const { activity, persona, ...props } = this.props;

    if (!activity) {
      return <div className="activity-error">No activity provided</div>;
    }

    // This will be implemented when we have the registry
    return <div className="activity-placeholder">Activity type: {activity.type}</div>;
  }
}

/**
 * Higher-order component to create activity components
 */
export function createActivityComponent<TProps extends ActivityComponentProps>(
  Component: React.ComponentType<TProps>
): React.ComponentType<TProps> {
  const WrappedComponent = (props: TProps) => {
    return (
      <div className="activity-component-wrapper" data-activity-type={props.activity?.type}>
        <Component {...props} />
      </div>
    );
  };

  WrappedComponent.displayName = `ActivityComponent(${Component.displayName || Component.name})`;

  return WrappedComponent;
}
