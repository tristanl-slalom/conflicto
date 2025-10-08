/**
 * Polling Activity Registration
 *
 * Registers the polling activity with all its persona components.
 */

import { registerActivity } from '@/lib/activity-framework';
import {
  PollingAdmin,
  PollingViewer,
  PollingParticipant
} from '@/components/activities/PollingActivity';

// Register the polling activity with persona-specific components
registerActivity(
  'polling',
  'Polling Activity',
  'Interactive polling with real-time results and multi-persona support',
  PollingAdmin, // Default component (admin)
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
        question: {
          type: 'string',
          description: 'The polling question',
          maxLength: 500,
        },
        options: {
          type: 'array',
          items: {
            type: 'string',
            maxLength: 200,
          },
          minItems: 2,
          maxItems: 10,
          description: 'Available answer options',
        },
        allow_multiple_choice: {
          type: 'boolean',
          default: false,
          description: 'Allow participants to select multiple options',
        },
        show_live_results: {
          type: 'boolean',
          default: true,
          description: 'Display results in real-time to viewers',
        },
        anonymous_voting: {
          type: 'boolean',
          default: true,
          description: 'Hide participant identities in responses',
        },
      },
      required: ['question', 'options'],
      additionalProperties: false,
    },
  }
);

console.log('[PollingActivity] Registered with activity framework');
