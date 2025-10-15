import type { SessionStatusCardProps } from '../../types/admin';
import { formatDistanceToNow } from 'date-fns';

export const SessionStatusCard = ({
  session,
  isLoading = false,
  onRefresh,
  className = ''
}: SessionStatusCardProps) => {
  if (isLoading) {
    return (
      <div className={`bg-card rounded-lg p-6 border border-border ${className}`}>
        <h2 className="text-lg font-medium text-foreground mb-4">Session Status</h2>
        <div className="space-y-4">
          <div className="animate-pulse">
            <div className="h-4 bg-slate-600 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-slate-600 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className={`bg-card rounded-lg p-6 border border-border ${className}`}>
        <h2 className="text-lg font-medium text-foreground mb-4">Session Status</h2>
        <div className="text-center py-8">
          <p className="text-muted-foreground">No active session</p>
          <p className="text-sm text-gray-500 mt-1">Create a session to get started</p>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-900 text-green-300';
      case 'completed':
        return 'bg-gray-900 text-gray-300';
      case 'draft':
      default:
        return 'bg-blue-900 text-blue-300';
    }
  };

  const getStatusActions = (status: string) => {
    switch (status) {
      case 'draft':
        return (
          <button className="w-full bg-green-600 hover:bg-green-700 text-foreground py-2 px-4 rounded-md transition-colors">
            Start Session
          </button>
        );
      case 'active':
        return (
          <div className="space-y-2">
            <button className="w-full bg-red-600 hover:bg-red-700 text-foreground py-2 px-4 rounded-md transition-colors">
              End Session
            </button>
            <button className="w-full bg-secondary hover:bg-secondary/90 text-foreground py-2 px-4 rounded-md transition-colors">
              Pause Session
            </button>
          </div>
        );
      case 'completed':
        return (
          <button className="w-full bg-secondary hover:bg-secondary/90 text-foreground py-2 px-4 rounded-md transition-colors">
            View Results
          </button>
        );
      default:
        return null;
    }
  };

  return (
    <div className={`bg-card rounded-lg p-6 border border-border ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-medium text-foreground">Session Status</h2>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="text-sm text-muted-foreground hover:text-gray-300 transition-colors"
          >
            Refresh
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Session Title */}
        <div>
          <h3 className="text-foreground font-medium text-lg mb-1 line-clamp-2">
            {session.title}
          </h3>
          {session.description && (
            <p className="text-muted-foreground text-sm line-clamp-3">
              {session.description}
            </p>
          )}
        </div>

        {/* Status Information */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-300">Status</span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(session.status)}`}>
              {session.status.charAt(0).toUpperCase() + session.status.slice(1)}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-gray-300">Session ID</span>
            <span className="text-foreground font-mono text-sm">{session.id}</span>
          </div>

          {session.participant_count !== undefined && (
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Participants</span>
              <span className="text-foreground font-mono">{session.participant_count}</span>
            </div>
          )}

          {session.activity_count !== undefined && (
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Activities</span>
              <span className="text-foreground font-mono">{session.activity_count}</span>
            </div>
          )}

          {session.max_participants && (
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Max Participants</span>
              <span className="text-foreground font-mono">{session.max_participants}</span>
            </div>
          )}

          <div className="flex items-center justify-between">
            <span className="text-gray-300">Created</span>
            <span className="text-foreground text-sm">
              {formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}
            </span>
          </div>

          {session.started_at && (
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Started</span>
              <span className="text-foreground text-sm">
                {formatDistanceToNow(new Date(session.started_at), { addSuffix: true })}
              </span>
            </div>
          )}

          {session.completed_at && (
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Completed</span>
              <span className="text-foreground text-sm">
                {formatDistanceToNow(new Date(session.completed_at), { addSuffix: true })}
              </span>
            </div>
          )}
        </div>

        {/* QR Code Section */}
        {session.qr_code && session.status === 'active' && (
          <div className="pt-4 border-t border-slate-600">
            <p className="text-sm text-gray-300 mb-2">Join Code:</p>
            <div className="bg-muted p-3 rounded-md">
              <code className="text-foreground font-mono text-sm break-all">
                {session.qr_code}
              </code>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="pt-4 border-t border-slate-600">
          {getStatusActions(session.status)}
        </div>
      </div>
    </div>
  );
};
