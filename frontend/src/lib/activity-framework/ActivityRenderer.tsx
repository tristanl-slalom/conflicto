/**
 * Activity Renderer Component
 *
 * Universal component that dynamically renders the appropriate persona interface
 * for any registered activity type based on the current user's role.
 */

import { useState } from 'react';
import React from 'react';
import { Activity, ActivityStatus, ActivityPersona } from '@/lib/activity-framework/types';
import { ActivityRegistry } from '@/lib/activity-framework';

interface ActivityRendererProps {
  activity: Activity;
  status?: ActivityStatus;
  persona: ActivityPersona;
  onConfigUpdate?: (config: Record<string, unknown>) => void;
  onSave?: () => void;
  onSubmitResponse?: (response: unknown) => void;
  onRefresh?: () => void;
  className?: string;
}

export default function ActivityRenderer({
  activity,
  status,
  persona,
  onConfigUpdate,
  onSave,
  onSubmitResponse,
  onRefresh,
  className = ''
}: ActivityRendererProps) {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Get the registered activity component
  const activityType = ActivityRegistry.getInstance().get(activity.type);

  if (!activityType) {
    return (
      <div className={`activity-renderer-error ${className}`}>
        <div className="flex items-center justify-center min-h-96 bg-red-50 border border-red-200 rounded-lg">
          <div className="text-center p-6">
            <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-red-800 mb-2">
              Unknown Activity Type
            </h3>
            <p className="text-red-700 mb-4">
              Activity type "{activity.type}" is not registered with the framework.
            </p>
            <p className="text-sm text-red-600">
              Available types: {ActivityRegistry.getInstance().getAllIds().join(', ')}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`activity-renderer-error ${className}`}>
        <div className="flex items-center justify-center min-h-96 bg-red-50 border border-red-200 rounded-lg">
          <div className="text-center p-6">
            <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-red-800 mb-2">
              Rendering Error
            </h3>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={() => {
                setError(null);
                setIsLoading(false);
              }}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Prepare props based on persona
  const baseProps = {
    activity,
    configuration: activity.configuration || {},
  };

  let personaProps = {};

  try {
    switch (persona) {
      case 'admin':
        personaProps = {
          ...baseProps,
          onConfigUpdate: onConfigUpdate || (() => {}),
          onSave: onSave || (() => {}),
          validation: status ? { valid: true, errors: [] } : undefined,
          isLoading,
        };
        break;

      case 'viewer':
        personaProps = {
          ...baseProps,
          responses: [],
          results: status?.results ? {
            results: status.results,
            last_updated: status.last_updated
          } : undefined,
          status: status?.status,
          liveResults: true,
          isLoading,
          onRefresh,
        };
        break;

      case 'participant':
        personaProps = {
          ...baseProps,
          onSubmitResponse: onSubmitResponse || (() => {}),
          canSubmit: status?.status === 'active',
          hasSubmitted: (status?.response_count || 0) > 0,
          isSubmitting: isLoading,
          lastResponse: undefined, // Would come from API
        };
        break;

      default:
        throw new Error(`Invalid persona: ${persona}`);
    }

    // Create the component with error boundary
    const ComponentToRender = ActivityRegistry.getInstance().getPersonaComponent(activity.type, persona);

    if (!ComponentToRender) {
      setError(`No ${persona} component found for activity type: ${activity.type}`);
      return null;
    }

    return (
      <div className={`activity-renderer activity-renderer--${persona} ${className}`}>
        <ErrorBoundary
          onError={(error: Error) => setError(error.message)}
          fallback={
            <div className="p-6 text-center">
              <p className="text-red-600">Component rendering failed</p>
            </div>
          }
        >
          <ComponentToRender {...personaProps} />
        </ErrorBoundary>
      </div>
    );
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Unknown rendering error');
    return null;
  }
}

// Simple error boundary component
interface ErrorBoundaryProps {
  children: React.ReactNode;
  onError: (error: Error) => void;
  fallback: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
        return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Activity component error:', error, errorInfo);
    this.props.onError(error);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}
