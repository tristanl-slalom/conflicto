import { useSessionManagement } from '../../hooks/useSessionManagement';
import type { SessionListProps } from '../../types/admin';
import type { SessionResponse } from '../../api/generated';
import { formatDistanceToNow } from 'date-fns';

export const SessionList = ({
  onSessionSelect,
  showActions = true,
  maxItems,
  className = ''
}: SessionListProps) => {
  const { sessions, isLoadingSessions, sessionsError, refetchSessions } = useSessionManagement();

  const displaySessions = maxItems ? sessions.slice(0, maxItems) : sessions;

  if (isLoadingSessions) {
    return (
      <div className={`bg-slate-800 rounded-lg p-6 border border-slate-700 ${className}`}>
        <h2 className="text-lg font-medium text-white mb-4">Recent Sessions</h2>
        <div className="flex items-center justify-center py-8">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="ml-2 text-gray-400">Loading sessions...</span>
        </div>
      </div>
    );
  }

  if (sessionsError) {
    return (
      <div className={`bg-slate-800 rounded-lg p-6 border border-slate-700 ${className}`}>
        <h2 className="text-lg font-medium text-white mb-4">Recent Sessions</h2>
        <div className="text-center py-8">
          <p className="text-red-400 mb-4">Failed to load sessions</p>
          <button
            onClick={() => refetchSessions()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-slate-800 rounded-lg p-6 border border-slate-700 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-medium text-white">Recent Sessions</h2>
        <button
          onClick={() => refetchSessions()}
          className="text-sm text-gray-400 hover:text-gray-300 transition-colors"
        >
          Refresh
        </button>
      </div>

      {displaySessions.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-400">No sessions created yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {displaySessions.map((session: SessionResponse) => (
            <div
              key={session.id}
              className="bg-slate-700 rounded-lg p-4 border border-slate-600 hover:border-slate-500 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-medium truncate">
                    {session.title}
                  </h3>
                  {session.description && (
                    <p className="text-gray-400 text-sm mt-1 line-clamp-2">
                      {session.description}
                    </p>
                  )}
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                    <span>ID: {session.id}</span>
                    <span>
                      Created {formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 ml-4">
                  {/* Session Status Badge */}
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      session.status === 'active'
                        ? 'bg-green-900 text-green-300'
                        : session.status === 'completed'
                        ? 'bg-gray-900 text-gray-300'
                        : 'bg-blue-900 text-blue-300'
                    }`}
                  >
                    {session.status}
                  </span>

                  {showActions && (
                    <div className="flex gap-1">
                      <button
                        onClick={() => onSessionSelect?.(session)}
                        className="p-1.5 text-gray-400 hover:text-white hover:bg-slate-600 rounded transition-colors"
                        title="View session"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </button>
                      
                      {session.status === 'draft' && (
                        <button
                          className="p-1.5 text-gray-400 hover:text-green-400 hover:bg-slate-600 rounded transition-colors"
                          title="Start session"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m-6-8h1m4 0h1M9 22h6a2 2 0 002-2V4a2 2 0 00-2-2H9a2 2 0 00-2 2v16a2 2 0 002 2z" />
                          </svg>
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {maxItems && sessions.length > maxItems && (
        <div className="mt-4 text-center">
          <button className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
            View all sessions ({sessions.length})
          </button>
        </div>
      )}
    </div>
  );
};