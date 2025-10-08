/**
 * Frontend activity registry for managing available activity types
 */

import { BaseActivityComponent } from './activity-framework/BaseActivityComponent';

export interface ActivityTypeDefinition {
  id: string;
  name: string;
  description: string;
  component: new () => BaseActivityComponent;
  schema?: Record<string, unknown>;
}

class ActivityRegistry {
  private registry = new Map<string, ActivityTypeDefinition>();

  /**
   * Register an activity type with the frontend registry
   */
  register(definition: ActivityTypeDefinition) {
    if (this.registry.has(definition.id)) {
      console.warn(`Activity type ${definition.id} is already registered`);
      return;
    }

    // Validate that the component implements all required methods
    const instance = new definition.component();
    const requiredMethods: (keyof BaseActivityComponent)[] = ['renderAdmin', 'renderViewer', 'renderParticipant'];

    for (const method of requiredMethods) {
      if (typeof instance[method] !== 'function') {
        throw new Error(`Activity component ${definition.id} must implement ${String(method)} method`);
      }
    }

    this.registry.set(definition.id, definition);
    console.log(`Registered activity type: ${definition.id}`);
  }

  /**
   * Get activity type definition by ID
   */
  get(activityType: string): ActivityTypeDefinition | undefined {
    return this.registry.get(activityType);
  }

  /**
   * Get all registered activity types
   */
  getAll(): ActivityTypeDefinition[] {
    return Array.from(this.registry.values());
  }

  /**
   * Check if activity type is registered
   */
  has(activityType: string): boolean {
    return this.registry.has(activityType);
  }

  /**
   * Create instance of activity component
   */
  createInstance(activityType: string): BaseActivityComponent | null {
    const definition = this.get(activityType);
    if (!definition) {
      console.error(`Activity type ${activityType} not found in registry`);
      return null;
    }

    try {
      return new definition.component();
    } catch (error) {
      console.error(`Failed to create instance of ${activityType}:`, error);
      return null;
    }
  }

  /**
   * Get list of activity type IDs
   */
  getTypeIds(): string[] {
    return Array.from(this.registry.keys());
  }

  /**
   * Clear registry (for testing)
   */
  clear() {
    this.registry.clear();
  }
}

// Global registry instance
export const activityRegistry = new ActivityRegistry();

// Auto-register activity types when they are imported
export function registerActivityType(definition: ActivityTypeDefinition) {
  activityRegistry.register(definition);
}
