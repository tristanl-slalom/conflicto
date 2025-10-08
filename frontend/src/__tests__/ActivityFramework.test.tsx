/**
 * Activity Framework Integration Test
 *
 * Tests the core functionality of the activity framework.
 */

import { describe, it, expect, beforeEach } from 'vitest';

// Import framework components
import { ActivityRegistry } from '@/lib/activity-framework';

// Import polling activity components directly
import {
  PollingAdmin,
  PollingViewer,
  PollingParticipant
} from '@/components/activities/PollingActivity';

describe('Activity Framework Core Tests', () => {
  beforeEach(() => {
    // Clear any previous registrations for clean tests
    ActivityRegistry.getInstance().clear();
  });

  describe('Activity Registry', () => {
    it('should register activity types', () => {
      const registry = ActivityRegistry.getInstance();

      // Register polling activity for tests
      registry.register(
        'polling',
        'Polling Activity',
        'Interactive polling with real-time results',
        PollingAdmin,
        {
          version: '1.0.0',
          components: {
            admin: PollingAdmin,
            viewer: PollingViewer,
            participant: PollingParticipant,
          },
          schema: {
            type: 'object',
            properties: {
              question: { type: 'string' },
              options: { type: 'array', items: { type: 'string' } },
            },
            required: ['question', 'options'],
          },
        }
      );

      expect(registry.has('polling')).toBe(true);

      const pollingType = registry.get('polling');
      expect(pollingType).toBeDefined();
      expect(pollingType?.name).toBe('Polling Activity');
      expect(pollingType?.components).toBeDefined();
      expect(pollingType?.components?.admin).toBeDefined();
      expect(pollingType?.components?.viewer).toBeDefined();
      expect(pollingType?.components?.participant).toBeDefined();
    });

    it('should provide activity type metadata', () => {
      const registry = ActivityRegistry.getInstance();

      // Register activity
      registry.register(
        'polling',
        'Polling Activity',
        'Interactive polling',
        PollingAdmin,
        {
          version: '1.0.0',
          components: {
            admin: PollingAdmin,
            viewer: PollingViewer,
            participant: PollingParticipant,
          },
        }
      );

      const metadata = registry.getMetadata('polling');

      expect(metadata).toBeDefined();
      expect(metadata?.id).toBe('polling');
      expect(metadata?.name).toBe('Polling Activity');
    });

    it('should validate all registered activity types', () => {
      const registry = ActivityRegistry.getInstance();

      // Register activity
      registry.register(
        'polling',
        'Polling Activity',
        'Interactive polling',
        PollingAdmin,
        {
          version: '1.0.0',
          components: {
            admin: PollingAdmin,
            viewer: PollingViewer,
            participant: PollingParticipant,
          },
        }
      );

      const validation = registry.validate();

      expect(validation.valid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });

    it('should support registering new activity types', () => {
      const registry = ActivityRegistry.getInstance();

      // Mock custom activity component
      const CustomActivity = () => 'Custom Activity';

      // Register new activity type
      registry.register(
        'custom',
        'Custom Activity',
        'A custom test activity',
        CustomActivity,
        {
          version: '1.0.0',
          components: {
            admin: CustomActivity,
            viewer: CustomActivity,
            participant: CustomActivity,
          }
        }
      );

      expect(registry.has('custom')).toBe(true);
      expect(registry.getAllIds()).toContain('custom');
    });

    it('should prevent duplicate registrations', () => {
      const registry = ActivityRegistry.getInstance();
      const DuplicateActivity = () => 'Duplicate';

      // First registration should succeed
      registry.register('test-duplicate', 'Test', 'Test activity', DuplicateActivity);

      // Second registration should throw error
      expect(() => {
        registry.register('test-duplicate', 'Test 2', 'Another test', DuplicateActivity);
      }).toThrow("Activity type 'test-duplicate' is already registered");
    });

    it('should return all registered activity IDs', () => {
      const registry = ActivityRegistry.getInstance();
      const TestActivity = () => 'Test';

      registry.register('test1', 'Test 1', 'First test', TestActivity);
      registry.register('test2', 'Test 2', 'Second test', TestActivity);

      const ids = registry.getAllIds();
      expect(ids).toContain('test1');
      expect(ids).toContain('test2');
      expect(ids).toHaveLength(2);
    });

    it('should clear all registrations', () => {
      const registry = ActivityRegistry.getInstance();
      const TestActivity = () => 'Test';

      registry.register('test', 'Test', 'Test activity', TestActivity);
      expect(registry.has('test')).toBe(true);

      registry.clear();
      expect(registry.has('test')).toBe(false);
      expect(registry.getAllIds()).toHaveLength(0);
    });
  });
});
