import React from 'react';
import { useGetSessionParticipantsApiV1SessionsSessionIdParticipantsGet, type ParticipantStatus } from '../api/generated';

interface ParticipantListProps {
  sessionId: number;
  className?: string;
}

const ParticipantList: React.FC<ParticipantListProps> = ({ sessionId, className }) => {
  // Use the generated React Query hook with polling
  const { 
    data, 
    isLoading: loading, 
    error 
  } = useGetSessionParticipantsApiV1SessionsSessionIdParticipantsGet(
    sessionId,
    {
      query: {
        refetchInterval: 10000, // Poll every 10 seconds
        refetchIntervalInBackground: true,
      }
    }
  );

  const participants = (data?.status === 200 && 'participants' in data.data) 
    ? data.data.participants 
    : [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-900 text-green-300';
      case 'idle':
        return 'bg-yellow-900 text-yellow-300';
      case 'disconnected':
        return 'bg-red-900 text-red-300';
      default:
        return 'bg-gray-900 text-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return '●';
      case 'idle':
        return '◐';
      case 'disconnected':
        return '○';
      default:
        return '?';
    }
  };

  if (loading) {
    return (
      <div className={`${className || ''}`}>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
          <span className="ml-2 text-gray-400">Loading participants...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className || ''}`}>
        <div className="text-center py-8">
          <div className="text-red-400 mb-2">⚠️ Error loading participants</div>
          <div className="text-sm text-gray-500">
            {'error' in error && typeof error.error === 'string' 
              ? error.error 
              : 'Failed to load participants'}
          </div>
        </div>
      </div>
    );
  }

  if (participants.length === 0) {
    return (
      <div className={`${className || ''}`}>
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">No participants yet</div>
          <div className="text-sm text-gray-500">Share the QR code to invite people to join</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className || ''}`}>
      <div className="space-y-3">
        {participants.map((participant: ParticipantStatus) => (
          <div
            key={participant.participant_id}
            className="flex items-center justify-between p-3 bg-slate-700 rounded-lg border border-slate-600"
          >
            <div className="flex items-center space-x-3">
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(participant.status)}`}>
                <span className="mr-1">{getStatusIcon(participant.status)}</span>
                {participant.status}
              </div>
              <div>
                <div className="text-white font-medium">{participant.nickname}</div>
                <div className="text-xs text-gray-400">
                  Joined: {new Date(participant.joined_at).toLocaleTimeString()}
                </div>
              </div>
            </div>
            <div className="text-xs text-gray-400">
              Last seen: {new Date(participant.last_seen).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-center">
        <div className="text-sm text-gray-400">
          Total: {participants.length} participant{participants.length !== 1 ? 's' : ''}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Updates every 10 seconds
        </div>
      </div>
    </div>
  );
};

export default ParticipantList;