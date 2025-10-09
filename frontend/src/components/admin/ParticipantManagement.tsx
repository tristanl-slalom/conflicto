import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Copy, ExternalLink, QrCode, Users, UserMinus, AlertTriangle, CheckCircle } from 'lucide-react';
import { SessionDetail, getSessionParticipantsApiV1SessionsSessionIdParticipantsGet, removeParticipantApiV1ParticipantsParticipantIdDelete } from '../../api/generated';

interface ParticipantManagementProps {
  session?: SessionDetail;
  className?: string;
}

export function ParticipantManagement({ session, className = '' }: ParticipantManagementProps) {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Get participants list with real-time polling
  const { data: participantsResponse } = useQuery({
    queryKey: ['session-participants', session?.id],
    queryFn: () => {
      if (!session?.id) throw new Error('No session ID');
      return getSessionParticipantsApiV1SessionsSessionIdParticipantsGet(session.id);
    },
    enabled: !!session?.id,
    refetchInterval: session?.status === 'active' || session?.status === 'paused' ? 3000 : 10000, // Faster polling for active sessions
    refetchIntervalInBackground: true,
    staleTime: 1000, // Consider data stale after 1 second
  });

  const participants = participantsResponse && 'data' in participantsResponse && participantsResponse.data && 'participants' in participantsResponse.data
    ? participantsResponse.data.participants || []
    : [];

  // Remove participant mutation
  const removeParticipantMutation = useMutation({
    mutationFn: (participantId: string) => removeParticipantApiV1ParticipantsParticipantIdDelete(participantId),
    onSuccess: () => {
      // Refetch participants list
      queryClient.invalidateQueries({ queryKey: ['session-participants', session?.id] });
      // Also refresh session data to update participant count
      queryClient.invalidateQueries({ queryKey: ['session', session?.id] });
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
    onError: (error) => {
      console.error('Failed to remove participant:', error);
    },
  });

  const handleCopyCode = async (code: string, type: 'qr' | 'admin' | 'url') => {
    try {
      const textToCopy = type === 'url'
        ? `${window.location.origin}/join/${code}`
        : code;

      await navigator.clipboard.writeText(textToCopy);
      setCopiedCode(type);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const getJoinUrl = () => {
    if (!session?.qr_code) return '';
    return `${window.location.origin}/join/${session.qr_code}`;
  };

  const handleRemoveParticipant = async (participantId: string, participantNickname: string) => {
    if (window.confirm(`Remove ${participantNickname} from the session? This action cannot be undone.`)) {
      try {
        await removeParticipantMutation.mutateAsync(participantId);
      } catch (error) {
        console.error('Failed to remove participant:', error);
        alert('Failed to remove participant. Please try again.');
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'online':
        return 'bg-green-900/30 text-green-400';
      case 'idle':
        return 'bg-yellow-900/30 text-yellow-400';
      case 'disconnected':
        return 'bg-red-900/30 text-red-400';
      default:
        return 'bg-slate-600/30 text-slate-400';
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
        <h2 className="text-lg font-medium text-white flex items-center gap-2">
          <Users className="w-5 h-5" />
          Participant Management
        </h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-400">
            {participants.length} participants
          </span>
          {(session?.status === 'active' || session?.status === 'paused') && (
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" title="Live updates" />
          )}
        </div>
      </div>

      {/* QR Code and Join Information */}
      {session.qr_code && (
        <div className="mb-6 p-4 bg-slate-700/50 rounded-lg border border-slate-600">
          <h3 className="text-white font-medium mb-3 flex items-center gap-2">
            <QrCode className="w-4 h-4" />
            Join Information
          </h3>

          <div className="space-y-3">
            {/* QR Code */}
            <div>
              <label className="block text-sm text-slate-300 mb-1">QR Code</label>
              <div className="flex items-center gap-2">
                <code className="flex-1 px-3 py-2 bg-slate-800 rounded text-white text-sm font-mono">
                  {session.qr_code}
                </code>
                <button
                  onClick={() => handleCopyCode(session.qr_code!, 'qr')}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded transition-colors"
                  title="Copy QR code"
                >
                  {copiedCode === 'qr' ? (
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Join URL */}
            <div>
              <label className="block text-sm text-slate-300 mb-1">Join URL</label>
              <div className="flex items-center gap-2">
                <code className="flex-1 px-3 py-2 bg-slate-800 rounded text-white text-sm font-mono break-all">
                  {getJoinUrl()}
                </code>
                <button
                  onClick={() => handleCopyCode(session.qr_code!, 'url')}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded transition-colors"
                  title="Copy join URL"
                >
                  {copiedCode === 'url' ? (
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
                <a
                  href={getJoinUrl()}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded transition-colors"
                  title="Open join URL"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>

            {/* Admin Code */}
            {session.admin_code && (
              <div>
                <label className="block text-sm text-slate-300 mb-1">Admin Code</label>
                <div className="flex items-center gap-2">
                  <code className="flex-1 px-3 py-2 bg-slate-800 rounded text-white text-sm font-mono">
                    {session.admin_code}
                  </code>
                  <button
                    onClick={() => handleCopyCode(session.admin_code!, 'admin')}
                    className="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded transition-colors"
                    title="Copy admin code"
                  >
                    {copiedCode === 'admin' ? (
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Participants List */}
      <div>
        <h3 className="text-white font-medium mb-3">Active Participants</h3>

        {participants.length > 0 ? (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {participants.map((participant) => (
              <div
                key={participant.participant_id}
                className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">
                      {participant.nickname.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <div className="text-white font-medium">{participant.nickname}</div>
                    <div className="text-slate-400 text-xs">
                      Joined {new Date(participant.joined_at).toLocaleTimeString()}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(participant.status)}`}>
                    {participant.status}
                  </span>

                  <button
                    onClick={() => handleRemoveParticipant(participant.participant_id, participant.nickname)}
                    disabled={removeParticipantMutation.isPending}
                    className="p-1 text-slate-400 hover:text-red-400 hover:bg-slate-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Remove participant"
                  >
                    <UserMinus className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-slate-400">
            <div className="text-4xl mb-2">👥</div>
            <p>No participants yet</p>
            <p className="text-sm">Share the QR code to get started</p>
          </div>
        )}
      </div>

      {/* Error Display */}
      {removeParticipantMutation.error && (
        <div className="mt-4 p-3 bg-red-900/30 border border-red-500/30 rounded-lg">
          <div className="flex items-center text-red-400 text-sm">
            <AlertTriangle className="w-4 h-4 mr-2 flex-shrink-0" />
            <span>
              Failed to remove participant: {
                removeParticipantMutation.error instanceof Error
                  ? removeParticipantMutation.error.message
                  : 'Unknown error'
              }
            </span>
          </div>
        </div>
      )}

      {/* Session Status Info */}
      {session.status !== 'active' && (
        <div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-500/30 rounded-lg">
          <div className="flex items-center text-yellow-400 text-sm">
            <AlertTriangle className="w-4 h-4 mr-2 flex-shrink-0" />
            <span>
              {session.status === 'draft'
                ? 'Start the session to allow participants to join'
                : session.status === 'paused'
                ? 'Session is paused - participants cannot join'
                : 'Session is completed - no new participants can join'
              }
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
