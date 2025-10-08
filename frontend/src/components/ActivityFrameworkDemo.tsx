/**
 * Activity Framework Demo
 *
 * Demonstrates the extensible activity framework with polling activity.
 */

import { useState } from 'react';
import { ActivityRenderer } from '@/lib/activity-framework';
import type { Activity, ActivityPersona } from '@/lib/activity-framework';

// Import polling activity registration to ensure it's loaded
import '@/components/activities/PollingActivity/register';

// Mock activity data for demonstration
const mockActivity: Activity = {
  id: 'demo-poll-1',
  session_id: 123,
  type: 'polling',
  title: 'Demo Poll Activity',
  description: 'A demonstration of the extensible activity framework',
  configuration: {
    question: 'Which programming language do you prefer for web development?',
    options: ['JavaScript', 'TypeScript', 'Python', 'Go', 'Rust'],
    allow_multiple_choice: false,
    show_live_results: true,
    anonymous_voting: true,
  },
  activity_metadata: {
    allow_multiple_responses: false,
    show_live_results: true,
    activity_type: 'polling',
  },
  status: 'active',
  state: 'active',
  order_index: 1,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const mockStatus = {
  activity_id: 'demo-poll-1',
  status: 'active',
  state: 'active' as const,
  response_count: 12,
  activity_metadata: {
    allow_multiple_responses: false,
    show_live_results: true,
    activity_type: 'polling',
    version: '1.0.0',
    last_response_at: new Date().toISOString(),
  },
  valid_transitions: ['pause', 'complete'],
  results: {
    type: 'poll_results',
    question: 'Which programming language do you prefer for web development?',
    options: ['JavaScript', 'TypeScript', 'Python', 'Go', 'Rust'],
    vote_counts: {
      'JavaScript': 4,
      'TypeScript': 6,
      'Python': 1,
      'Go': 1,
      'Rust': 0,
    },
    percentages: {
      'JavaScript': 33.3,
      'TypeScript': 50.0,
      'Python': 8.3,
      'Go': 8.3,
      'Rust': 0.0,
    },
    total_responses: 12,
    most_popular: ['TypeScript'],
    allow_multiple_choice: false,
    show_live_results: true,
    last_updated: new Date().toISOString(),
  },
  last_updated: new Date().toISOString(),
};

export default function ActivityFrameworkDemo() {
  const [currentPersona, setCurrentPersona] = useState<ActivityPersona>('admin');
  const [activity, setActivity] = useState(mockActivity);

  const handleConfigUpdate = (config: Record<string, unknown>) => {
    console.log('Configuration updated:', config);
    setActivity(prev => ({
      ...prev,
      configuration: config,
      updated_at: new Date().toISOString(),
    }));
  };

  const handleSave = () => {
    console.log('Saving activity configuration...');
    alert('Activity configuration saved! (This is a demo)');
  };

  const handleSubmitResponse = (response: unknown) => {
    console.log('Response submitted:', response);
    alert('Response submitted! (This is a demo)');
  };

  const handleRefresh = () => {
    console.log('Refreshing activity data...');
  };

  return (
    <div className="activity-framework-demo min-h-screen bg-gray-100">
      {/* Demo Controls */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Activity Framework Demo
          </h1>

          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-700">View as:</span>

            <div className="flex bg-gray-100 rounded-lg p-1">
              {(['admin', 'viewer', 'participant'] as ActivityPersona[]).map((persona) => (
                <button
                  key={persona}
                  onClick={() => setCurrentPersona(persona)}
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-colors capitalize ${
                    currentPersona === persona
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {persona}
                </button>
              ))}
            </div>

            <div className="text-sm text-gray-500 ml-auto">
              Activity Type: <span className="font-mono bg-gray-100 px-2 py-1 rounded">
                {activity.type}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Activity Renderer */}
      <div className="p-4">
        <div className="max-w-4xl mx-auto">
          <ActivityRenderer
            activity={activity}
            status={mockStatus}
            persona={currentPersona}
            onConfigUpdate={handleConfigUpdate}
            onSave={handleSave}
            onSubmitResponse={handleSubmitResponse}
            onRefresh={handleRefresh}
          />
        </div>
      </div>

      {/* Demo Info */}
      <div className="bg-blue-50 border-t border-blue-200 p-4 mt-8">
        <div className="max-w-4xl mx-auto">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            Framework Features Demonstrated
          </h3>

          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="bg-white rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">🔧 Admin Interface</h4>
              <ul className="text-gray-600 space-y-1">
                <li>• Configuration management</li>
                <li>• Real-time validation</li>
                <li>• Live preview</li>
                <li>• Settings toggles</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">📺 Viewer Interface</h4>
              <ul className="text-gray-600 space-y-1">
                <li>• Large screen display</li>
                <li>• Live result updates</li>
                <li>• Visual progress bars</li>
                <li>• Status indicators</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">📱 Participant Interface</h4>
              <ul className="text-gray-600 space-y-1">
                <li>• Mobile-optimized UI</li>
                <li>• Interactive voting</li>
                <li>• Response validation</li>
                <li>• Submission feedback</li>
              </ul>
            </div>
          </div>

          <div className="mt-4 p-3 bg-blue-100 rounded-md">
            <p className="text-blue-800 text-sm">
              <strong>Framework Benefits:</strong> This single polling activity automatically
              supports all three personas with appropriate interfaces. New activity types can be
              added by implementing the same pattern - just create the persona components and
              register them with the framework.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
