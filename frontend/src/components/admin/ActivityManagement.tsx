import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Settings, Trash2, GripVertical, AlertTriangle } from 'lucide-react';
import {
  SessionDetail,
  ActivityType,
  getActivityTypesApiV1ActivitiesTypesGet,
  createActivityApiV1SessionsSessionIdActivitiesPost,
  deleteActivityApiV1ActivitiesActivityIdDelete,
  ActivityCreate,
} from '../../api/generated';

interface ActivityManagementProps {
  session?: SessionDetail;
  onActivityChange?: () => void;
  className?: string;
}

interface ActivityFormData {
  type: ActivityType;
  title: string;
  description?: string;
  config: Record<string, any>;
}

export function ActivityManagement({ session, onActivityChange, className = '' }: ActivityManagementProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState<ActivityFormData>({
    type: ActivityType.poll,
    title: '',
    description: '',
    config: {},
  });

  const queryClient = useQueryClient();

  // Get available activity types
  const { data: activityTypesResponse } = useQuery({
    queryKey: ['activity-types'],
    queryFn: getActivityTypesApiV1ActivitiesTypesGet,
  });

  const activityTypes = activityTypesResponse && 'data' in activityTypesResponse
    ? activityTypesResponse.data?.activity_types || []
    : [];

  // Create activity mutation
  const createActivityMutation = useMutation({
    mutationFn: async (activityData: ActivityCreate) => {
      if (!session?.id) throw new Error('No session selected');
      return createActivityApiV1SessionsSessionIdActivitiesPost(session.id, activityData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['session', session?.id] });
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      onActivityChange?.();
      setIsCreating(false);
      setFormData({
        type: ActivityType.poll,
        title: '',
        description: '',
        config: {},
      });
    },
  });

  // Delete activity mutation
  const deleteActivityMutation = useMutation({
    mutationFn: (activityId: string) => deleteActivityApiV1ActivitiesActivityIdDelete(activityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['session', session?.id] });
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      onActivityChange?.();
    },
  });

  const handleCreateActivity = () => {
    if (!formData.title.trim()) return;

    const activityData: ActivityCreate = {
      type: formData.type,
      config: {
        title: formData.title,
        description: formData.description,
        ...getDefaultConfigForType(formData.type),
        ...formData.config,
      },
      order_index: (session?.activities?.length ?? 0),
    };

    createActivityMutation.mutate(activityData);
  };

  const handleDeleteActivity = (activityId: string) => {
    if (window.confirm('Are you sure you want to delete this activity?')) {
      deleteActivityMutation.mutate(activityId);
    }
  };

  const getDefaultConfigForType = (type: ActivityType): Record<string, any> => {
    switch (type) {
      case ActivityType.poll:
        return {
          question: 'Your poll question',
          options: ['Option 1', 'Option 2'],
          multiple_choice: false,
          anonymous: true,
        };
      case ActivityType.word_cloud:
        return {
          prompt: 'Enter your thoughts...',
          max_words: 100,
          min_word_length: 2,
        };
      case ActivityType.qa:
        return {
          prompt: 'Ask your questions',
          anonymous: true,
          moderation_required: false,
        };
      case ActivityType.planning_poker:
        return {
          story: 'Story to estimate',
          voting_options: ['1', '2', '3', '5', '8', '13', '21'],
          allow_revoting: true,
        };
      default:
        return {};
    }
  };

  const getActivityIcon = (type: ActivityType) => {
    switch (type) {
      case ActivityType.poll:
        return '📊';
      case ActivityType.word_cloud:
        return '☁️';
      case ActivityType.qa:
        return '❓';
      case ActivityType.planning_poker:
        return '🃏';
      default:
        return '📋';
    }
  };

  const getActivityDescription = (type: ActivityType) => {
    switch (type) {
      case ActivityType.poll:
        return 'Multiple choice questions with real-time results';
      case ActivityType.word_cloud:
        return 'Collect participant thoughts in a visual word cloud';
      case ActivityType.qa:
        return 'Q&A session with moderation options';
      case ActivityType.planning_poker:
        return 'Story point estimation using planning poker cards';
      default:
        return 'Interactive activity';
    }
  };

  if (!session) {
    return (
      <div className={`bg-slate-800 rounded-lg p-6 border border-slate-700 ${className}`}>
        <div className="flex items-center justify-center text-slate-400">
          <AlertTriangle className="w-5 h-5 mr-2" />
          <span>No session selected</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-slate-800 rounded-lg p-6 border border-slate-700 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-medium text-white">Activity Management</h2>
        <button
          onClick={() => setIsCreating(true)}
          className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Activity</span>
        </button>
      </div>

      {/* Activity List */}
      <div className="space-y-3 mb-6">
        {session.activities && session.activities.length > 0 ? (
          session.activities.map((activity) => (
            <div
              key={activity.id}
              className="flex items-center gap-3 p-4 bg-slate-700/50 rounded-lg border border-slate-600"
            >
              <div className="flex items-center gap-3 flex-1">
                <GripVertical className="w-4 h-4 text-slate-400 cursor-move" />
                <div className="text-2xl">{getActivityIcon(activity.activity_type)}</div>
                <div className="flex-1">
                  <div className="text-white font-medium">{activity.title}</div>
                  <div className="text-slate-400 text-sm">
                    {getActivityDescription(activity.activity_type)}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  activity.is_active
                    ? 'bg-green-900/30 text-green-400'
                    : 'bg-slate-600/30 text-slate-400'
                }`}>
                  {activity.is_active ? 'Active' : 'Draft'}
                </span>

                <button
                  onClick={() => {/* TODO: Open activity editor */}}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded-lg transition-colors"
                  title="Edit activity"
                >
                  <Settings className="w-4 h-4" />
                </button>

                <button
                  onClick={() => handleDeleteActivity(String(activity.id))}
                  disabled={activity.is_active || deleteActivityMutation.isPending}
                  className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Delete activity"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-slate-400">
            <div className="text-4xl mb-2">📋</div>
            <p>No activities yet</p>
            <p className="text-sm">Add your first activity to get started</p>
          </div>
        )}
      </div>

      {/* Create Activity Form */}
      {isCreating && (
        <div className="border-t border-slate-600 pt-6">
          <h3 className="text-white font-medium mb-4">Create New Activity</h3>

          <div className="space-y-4">
            {/* Activity Type Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Activity Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                {activityTypes.map((type) => (
                  <button
                    key={type.id}
                    onClick={() => setFormData(prev => ({ ...prev, type: type.id as ActivityType }))}
                    className={`p-3 text-left rounded-lg border transition-colors ${
                      formData.type === type.id
                        ? 'border-blue-500 bg-blue-900/30 text-blue-300'
                        : 'border-slate-600 bg-slate-700/50 text-slate-300 hover:border-slate-500'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">{getActivityIcon(type.id as ActivityType)}</span>
                      <span className="font-medium">{type.name}</span>
                    </div>
                    <div className="text-xs text-slate-400">{type.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Activity Title */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Title
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Enter activity title"
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-blue-500 focus:outline-none"
              />
            </div>

            {/* Activity Description */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Description (Optional)
              </label>
              <textarea
                value={formData.description || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Enter activity description"
                rows={2}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-blue-500 focus:outline-none resize-none"
              />
            </div>

            {/* Form Actions */}
            <div className="flex gap-3 pt-2">
              <button
                onClick={handleCreateActivity}
                disabled={!formData.title.trim() || createActivityMutation.isPending}
                className="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
              >
                {createActivityMutation.isPending ? 'Creating...' : 'Create Activity'}
              </button>
              <button
                onClick={() => setIsCreating(false)}
                className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white font-medium rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>

          {/* Error Display */}
          {createActivityMutation.error && (
            <div className="mt-4 p-3 bg-red-900/30 border border-red-500/30 rounded-lg">
              <div className="flex items-center text-red-400 text-sm">
                <AlertTriangle className="w-4 h-4 mr-2 flex-shrink-0" />
                <span>
                  Failed to create activity: {
                    createActivityMutation.error instanceof Error
                      ? createActivityMutation.error.message
                      : 'Unknown error'
                  }
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
