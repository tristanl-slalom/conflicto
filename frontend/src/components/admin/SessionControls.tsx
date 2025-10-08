import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Play, Pause, Square, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { SessionStatus, type SessionDetail, type SessionUpdate, updateSessionApiV1SessionsSessionIdPut } from '../../api/generated';

interface SessionControlsProps {
  session?: SessionDetail;
  onStatusChange?: (newStatus: SessionStatus) => void;
  className?: string;
}

export function SessionControls({ session, onStatusChange, className = '' }: SessionControlsProps) {
  const [isConfirming, setIsConfirming] = useState<SessionStatus | null>(null);
  const queryClient = useQueryClient();

  const updateStatusMutation = useMutation({
    mutationFn: async (newStatus: SessionStatus) => {
      if (!session?.id) throw new Error('No session selected');

      const updateData: SessionUpdate = { status: newStatus };
      return updateSessionApiV1SessionsSessionIdPut(session.id, updateData);
    },
    onSuccess: (response) => {
      // Invalidate and refetch session data
      queryClient.invalidateQueries({ queryKey: ['session', session?.id] });
      queryClient.invalidateQueries({ queryKey: ['sessions'] });

      // Type guard to check if response has session data
      if (onStatusChange && 'data' in response && response.data && 'status' in response.data) {
        onStatusChange(response.data.status);
      }

      setIsConfirming(null);
    },
    onError: (error) => {
      console.error('Failed to update session status:', error);
      setIsConfirming(null);
    },
  });

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

  const canStart = session.status === SessionStatus.draft && (session.activity_count ?? 0) > 0;
  const canPause = session.status === SessionStatus.active;
  const canResume = session.status === SessionStatus.paused;
  const canStop = session.status === SessionStatus.active || session.status === SessionStatus.paused;

  const handleStatusChange = (newStatus: SessionStatus) => {
    // Show confirmation for potentially destructive actions
    if (newStatus === SessionStatus.completed) {
      setIsConfirming(newStatus);
    } else {
      updateStatusMutation.mutate(newStatus);
    }
  };

  const confirmStatusChange = () => {
    if (isConfirming) {
      updateStatusMutation.mutate(isConfirming);
    }
  };

  const getStatusIcon = (status: SessionStatus) => {
    switch (status) {
      case SessionStatus.draft:
        return <Clock className="w-4 h-4" />;
      case SessionStatus.active:
        return <Play className="w-4 h-4" />;
      case SessionStatus.paused:
        return <Pause className="w-4 h-4" />;
      case SessionStatus.completed:
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: SessionStatus) => {
    switch (status) {
      case SessionStatus.draft:
        return 'text-slate-400 bg-slate-700/50';
      case SessionStatus.active:
        return 'text-green-400 bg-green-900/30';
      case SessionStatus.paused:
        return 'text-yellow-400 bg-yellow-900/30';
      case SessionStatus.completed:
        return 'text-blue-400 bg-blue-900/30';
      default:
        return 'text-slate-400 bg-slate-700/50';
    }
  };

  return (
    <div className={`bg-slate-800 rounded-lg p-6 border border-slate-700 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-medium text-white">Session Controls</h2>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(session.status)}`}>
          {getStatusIcon(session.status)}
          <span className="capitalize">{session.status}</span>
        </div>
      </div>

      {/* Session Info */}
      <div className="mb-6 p-4 bg-slate-700/50 rounded-lg">
        <div className="text-sm text-slate-300 space-y-1">
          <div className="flex justify-between">
            <span>Activities:</span>
            <span className="text-white">{session.activity_count}</span>
          </div>
          <div className="flex justify-between">
            <span>Participants:</span>
            <span className="text-white">{session.participant_count}</span>
          </div>
          {session.started_at && (
            <div className="flex justify-between">
              <span>Started:</span>
              <span className="text-white">
                {new Date(session.started_at).toLocaleTimeString()}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Validation Messages */}
      {session.status === SessionStatus.draft && session.activity_count === 0 && (
        <div className="mb-4 p-3 bg-yellow-900/30 border border-yellow-500/30 rounded-lg">
          <div className="flex items-center text-yellow-400 text-sm">
            <AlertTriangle className="w-4 h-4 mr-2 flex-shrink-0" />
            <span>Add activities before starting the session</span>
          </div>
        </div>
      )}

      {/* Control Buttons */}
      <div className="space-y-3">
        {session.status === SessionStatus.draft && (
          <button
            onClick={() => handleStatusChange(SessionStatus.active)}
            disabled={!canStart || updateStatusMutation.isPending}
            className={`w-full flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium transition-colors ${
              canStart
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-slate-600 text-slate-400 cursor-not-allowed'
            }`}
          >
            <Play className="w-4 h-4" />
            {updateStatusMutation.isPending ? 'Starting...' : 'Start Session'}
          </button>
        )}

        {session.status === SessionStatus.active && (
          <>
            <button
              onClick={() => handleStatusChange(SessionStatus.paused)}
              disabled={!canPause || updateStatusMutation.isPending}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium bg-yellow-600 hover:bg-yellow-700 text-white transition-colors"
            >
              <Pause className="w-4 h-4" />
              {updateStatusMutation.isPending ? 'Pausing...' : 'Pause Session'}
            </button>
          </>
        )}

        {session.status === SessionStatus.paused && (
          <button
            onClick={() => handleStatusChange(SessionStatus.active)}
            disabled={!canResume || updateStatusMutation.isPending}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium bg-green-600 hover:bg-green-700 text-white transition-colors"
          >
            <Play className="w-4 h-4" />
            {updateStatusMutation.isPending ? 'Resuming...' : 'Resume Session'}
          </button>
        )}

        {canStop && (
          <button
            onClick={() => handleStatusChange(SessionStatus.completed)}
            disabled={updateStatusMutation.isPending}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium bg-red-600 hover:bg-red-700 text-white transition-colors"
          >
            <Square className="w-4 h-4" />
            {updateStatusMutation.isPending ? 'Ending...' : 'End Session'}
          </button>
        )}
      </div>

      {/* Confirmation Dialog */}
      {isConfirming === SessionStatus.completed && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-md mx-4 border border-slate-700">
            <div className="flex items-center mb-4">
              <AlertTriangle className="w-6 h-6 text-red-400 mr-3" />
              <h3 className="text-lg font-medium text-white">End Session</h3>
            </div>
            <p className="text-slate-300 mb-6">
              Are you sure you want to end this session? This action cannot be undone and will prevent new participants from joining.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setIsConfirming(null)}
                className="flex-1 py-2 px-4 rounded-lg font-medium bg-slate-600 hover:bg-slate-500 text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmStatusChange}
                disabled={updateStatusMutation.isPending}
                className="flex-1 py-2 px-4 rounded-lg font-medium bg-red-600 hover:bg-red-700 text-white transition-colors"
              >
                {updateStatusMutation.isPending ? 'Ending...' : 'End Session'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {updateStatusMutation.error && (
        <div className="mt-4 p-3 bg-red-900/30 border border-red-500/30 rounded-lg">
          <div className="flex items-center text-red-400 text-sm">
            <AlertTriangle className="w-4 h-4 mr-2 flex-shrink-0" />
            <span>
              Failed to update session: {
                updateStatusMutation.error instanceof Error
                  ? updateStatusMutation.error.message
                  : 'Unknown error'
              }
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
