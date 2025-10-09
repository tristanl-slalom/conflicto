import React from 'react';
import { Users, Clock } from 'lucide-react';
import { useGetSessionParticipantsApiV1SessionsSessionIdParticipantsGet, type ParticipantStatus } from '../../api/generated';

interface PreLobbyParticipantListProps {
  sessionId: number;
  className?: string;
}

const PreLobbyParticipantList: React.FC<PreLobbyParticipantListProps> = ({ 
  sessionId, 
  className = '' 
}) => {
  // Use the generated React Query hook with polling optimized for pre-lobby
  const { 
    data, 
    isLoading: loading, 
    error 
  } = useGetSessionParticipantsApiV1SessionsSessionIdParticipantsGet(
    sessionId,
    {
      query: {
        refetchInterval: 3000, // Poll every 3 seconds for real-time updates
        refetchIntervalInBackground: true,
        staleTime: 1000, // Consider data stale after 1 second
        retry: 1, // Only retry once on failure
        retryDelay: 2000, // Wait 2 seconds before retry
        refetchOnWindowFocus: false, // Don't refetch when window gains focus
      }
    }
  );

  const participants = (data?.status === 200 && 'participants' in data.data) 
    ? data.data.participants 
    : [];

  const getStatusIndicator = (status: string) => {
    switch (status) {
      case 'online':
        return <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>;
      case 'idle':
        return <div className="w-2 h-2 bg-amber-400 rounded-full"></div>;
      case 'disconnected':
        return <div className="w-2 h-2 bg-gray-400 rounded-full"></div>;
      default:
        return <div className="w-2 h-2 bg-gray-400 rounded-full"></div>;
    }
  };

  const formatJoinTime = (joinedAt: string) => {
    const time = new Date(joinedAt);
    return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className={`${className}`}>
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-500"></div>
            <span className="ml-3 text-gray-300">Loading participants...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className}`}>
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
          <div className="text-center py-8">
            <div className="text-red-400 mb-2">⚠️ Error loading participants</div>
            <div className="text-sm text-gray-500">
              Failed to load participant list. Please refresh the page.
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-purple-600/20 rounded-lg">
            <Users className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">
              Participants Waiting
            </h3>
            <p className="text-sm text-gray-400">
              {participants.length} participant{participants.length !== 1 ? 's' : ''} joined
            </p>
          </div>
        </div>

        {/* Participant Count Badge */}
        <div className="mb-6">
          <div className="inline-flex items-center space-x-2 bg-purple-600/20 border border-purple-500/30 rounded-full px-4 py-2">
            <Users className="w-4 h-4 text-purple-400" />
            <span className="text-purple-300 font-medium">
              {participants.length} waiting
            </span>
          </div>
        </div>

        {/* Participants List */}
        <div className="space-y-3">
          {participants.length === 0 ? (
            <div className="text-center py-8">
              <div className="mb-4">
                <Clock className="w-12 h-12 text-gray-500 mx-auto" />
              </div>
              <div className="text-gray-400 mb-2">You're the first one here!</div>
              <div className="text-sm text-gray-500">
                More participants will appear as they join
              </div>
            </div>
          ) : (
            participants.map((participant: ParticipantStatus, index) => (
              <div
                key={participant.participant_id}
                className="flex items-center justify-between p-4 bg-slate-700/50 border border-slate-600/50 rounded-lg hover:bg-slate-700/70 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  {getStatusIndicator(participant.status)}
                  <div>
                    <div className="font-medium text-white">
                      {participant.nickname}
                    </div>
                    <div className="text-sm text-gray-400">
                      Joined at {formatJoinTime(participant.joined_at)}
                    </div>
                  </div>
                </div>
                
                {/* Join order indicator */}
                <div className="text-xs text-gray-500 bg-slate-600/50 rounded-full px-2 py-1">
                  #{index + 1}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        {participants.length > 0 && (
          <div className="mt-6 pt-6 border-t border-slate-600/50">
            <div className="text-center text-sm text-gray-400">
              <Clock className="w-4 h-4 inline-block mr-1" />
              Updates every 3 seconds
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PreLobbyParticipantList;