/**
 * Activity Registry
 *
 * Manages registration and discovery of activity types on the frontend.
 */

import React from 'react';
import { ActivityTypeDefinition, ActivityError } from './types';
import { BaseActivityComponent } from './BaseActivityComponent';

export class ActivityRegistry {
  private static instance: ActivityRegistry;
  private registry = new Map<string, ActivityTypeDefinition>();

  private constructor() {}

  static getInstance(): ActivityRegistry {
    if (!ActivityRegistry.instance) {
      ActivityRegistry.instance = new ActivityRegistry();
    }
    return ActivityRegistry.instance;
  }

  /**
   * Register an activity type with the framework.
   */
  register(
    id: string,
    name: string,
    description: string,
    component: React.ComponentType<any>,
    options: {
      version?: string;
      schema?: Record<string, unknown>;
      components?: {
        admin?: React.ComponentType<any>;
        viewer?: React.ComponentType<any>;
        participant?: React.ComponentType<any>;
      };
    } = {}
  ): void {
    if (this.registry.has(id)) {
      throw new Error(`Activity type '${id}' is already registered`);
    }

    const definition: ActivityTypeDefinition = {
      id,
      name,
      description,
      version: options.version || '1.0.0',
      component,
      components: options.components,
      schema: options.schema,
    };

    this.registry.set(id, definition);

    if (process.env.NODE_ENV === 'development') {
      console.log(`[ActivityRegistry] Registered activity type: ${id}`);
    }
  }

  /**
   * Unregister an activity type.
   */
  unregister(id: string): boolean {
    const existed = this.registry.has(id);
    this.registry.delete(id);

    if (existed && process.env.NODE_ENV === 'development') {
      console.log(`[ActivityRegistry] Unregistered activity type: ${id}`);
    }

    return existed;
  }

  /**
   * Get a registered activity type definition.
   */
  get(activityType: string): ActivityTypeDefinition | undefined {
    return this.registry.get(activityType);
  }

  /**
   * Check if an activity type is registered.
   */
  has(activityType: string): boolean {
    return this.registry.has(activityType);
  }

  /**
   * Get all registered activity types.
   */
  getAll(): ActivityTypeDefinition[] {
    return Array.from(this.registry.values());
  }

  /**
   * Get all registered activity type IDs.
   */
  getAllIds(): string[] {
    return Array.from(this.registry.keys());
  }

  /**
   * Get activity type metadata by ID.
   */
  getMetadata(activityType: string): Omit<ActivityTypeDefinition, 'component'> | undefined {
    const definition = this.registry.get(activityType);
    if (!definition) return undefined;

    const { component, ...metadata } = definition;
    return metadata;
  }

  /**
   * Get activity component class for a type.
   */
  getComponent(activityType: string): React.ComponentType<any> | undefined {
    const definition = this.registry.get(activityType);
    return definition?.component;
  }

  /**
   * Get persona-specific component for an activity type.
   */
  getPersonaComponent(
    activityType: string,
    persona: 'admin' | 'viewer' | 'participant'
  ): React.ComponentType<any> | undefined {
    const definition = this.registry.get(activityType);
    if (!definition) return undefined;

    // First check if persona-specific components are available
    if (definition.components && definition.components[persona]) {
      return definition.components[persona];
    }

    // Fallback to main component if no persona-specific component
    return definition.component;
  }

  /**
   * Create an activity component instance.
   */
  createComponent(
    activityType: string,
    props: any
  ): React.ReactElement | null {
    const Component = this.getComponent(activityType);

    if (!Component) {
      const error: ActivityError = {
        code: 'UNKNOWN_ACTIVITY_TYPE',
        message: `Unknown activity type: ${activityType}`,
        details: { activityType, availableTypes: this.getAllIds() }
      };

      if (process.env.NODE_ENV === 'development') {
        console.error('[ActivityRegistry] Failed to create component:', error);
      }

      return null;
    }

    return React.createElement(Component, props);
  }

  /**
   * Validate that all registered activity types are properly configured.
   */
  validate(): { valid: boolean; errors: ActivityError[] } {
    const errors: ActivityError[] = [];

    for (const [id, definition] of this.registry.entries()) {
      // Check that component is provided
      if (!definition.component) {
        errors.push({
          code: 'MISSING_COMPONENT',
          message: `Activity type '${id}' is missing component`,
          details: { activityType: id }
        });
      }

      // Check that component extends BaseActivityComponent (if possible)
      try {
        const component = definition.component;
        if (component && component.prototype && !(component.prototype instanceof BaseActivityComponent)) {
          // This is a loose check since TypeScript components might not extend the class
          // We'll add this as a warning in development
          if (process.env.NODE_ENV === 'development') {
            console.warn(`[ActivityRegistry] Activity type '${id}' component should extend BaseActivityComponent`);
          }
        }
      } catch (e) {
        // Ignore validation errors for component inheritance
      }

      // Validate required fields
      if (!definition.name || !definition.description) {
        errors.push({
          code: 'INCOMPLETE_DEFINITION',
          message: `Activity type '${id}' is missing required fields`,
          details: {
            activityType: id,
            missing: [
              !definition.name ? 'name' : null,
              !definition.description ? 'description' : null
            ].filter(Boolean)
          }
        });
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Clear all registered activity types (primarily for testing).
   */
  clear(): void {
    this.registry.clear();

    if (process.env.NODE_ENV === 'development') {
      console.log('[ActivityRegistry] Cleared all activity types');
    }
  }

  /**
   * Get registry information for debugging.
   */
  getDebugInfo(): {
    totalRegistered: number;
    registeredTypes: string[];
    definitions: Record<string, Omit<ActivityTypeDefinition, 'component'>>;
  } {
    const definitions: Record<string, Omit<ActivityTypeDefinition, 'component'>> = {};

    for (const [id, definition] of this.registry.entries()) {
      const { component, ...metadata } = definition;
      definitions[id] = metadata;
    }

    return {
      totalRegistered: this.registry.size,
      registeredTypes: this.getAllIds(),
      definitions
    };
  }
}

// Create and export singleton instance
export const activityRegistry = ActivityRegistry.getInstance();

// Export convenience functions
export const registerActivity = (
  id: string,
  name: string,
  description: string,
  component: React.ComponentType<any>,
  options?: {
    version?: string;
    schema?: Record<string, unknown>;
    components?: {
      admin?: React.ComponentType<any>;
      viewer?: React.ComponentType<any>;
      participant?: React.ComponentType<any>;
    };
  }
) => activityRegistry.register(id, name, description, component, options);

export const getActivity = (activityType: string) => activityRegistry.get(activityType);

export const hasActivity = (activityType: string) => activityRegistry.has(activityType);

export const getAllActivities = () => activityRegistry.getAll();

export const createActivityComponent = (activityType: string, props: any) =>
  activityRegistry.createComponent(activityType, props);
