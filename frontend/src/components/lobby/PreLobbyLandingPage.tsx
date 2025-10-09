import React from 'react';
import { Smartphone, Users, Clock, Coffee } from 'lucide-react';
import { useGetSessionApiV1SessionsSessionIdGet } from '../../api/generated';
import SessionStatusIndicator from './SessionStatusIndicator';
import PreLobbyParticipantList from './PreLobbyParticipantList';

interface PreLobbyLandingPageProps {
  sessionId: number;
  nickname?: string;
}

const PreLobbyLandingPage: React.FC<PreLobbyLandingPageProps> = ({ 
  sessionId, 
  nickname 
}) => {
  // Fetch session details with polling for status changes
  const { 
    data: sessionData, 
    isLoading: loadingSession, 
    error: sessionError 
  } = useGetSessionApiV1SessionsSessionIdGet(
    sessionId,
    {
      query: {
        refetchInterval: 5000, // Poll every 5 seconds for session status changes
        refetchIntervalInBackground: true,
        retry: 1, // Only retry once on failure
        retryDelay: 2000, // Wait 2 seconds before retry
        refetchOnWindowFocus: false, // Don't refetch when window gains focus
      }
    }
  );

  const session = sessionData?.status === 200 ? sessionData.data : null;

  // Extract participant count from session data for consistency
  const participantCount = session?.participant_count || 0;

  if (loadingSession) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <div className="text-lg font-medium">Loading session...</div>
        </div>
      </div>
    );
  }

  if (sessionError || !session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold mb-4">Session Not Found</h1>
          <p className="text-gray-300 mb-6">
            The session you're trying to join could not be found or may have been removed.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <div className="bg-slate-800/80 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Smartphone className="w-4 h-4" />
              </div>
              <div>
                <h1 className="font-semibold">{session.title}</h1>
                {nickname && (
                  <p className="text-sm text-gray-400">Welcome, {nickname}!</p>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <Users className="w-4 h-4" />
              <span>{participantCount}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Left Column - Session Info and Status */}
          <div className="space-y-6">
            
            {/* Welcome Section */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Coffee className="w-8 h-8" />
                </div>
                <h2 className="text-2xl font-bold mb-3">Welcome to the Pre-Lobby!</h2>
                <p className="text-gray-300 leading-relaxed">
                  You've successfully joined <strong>{session.title}</strong>. 
                  The session hasn't started yet, but you can see who else is here waiting with you.
                </p>
              </div>
            </div>

            {/* Session Description */}
            {session.description && (
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-3 flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-purple-400" />
                  About This Session
                </h3>
                <p className="text-gray-300 leading-relaxed">
                  {session.description}
                </p>
              </div>
            )}

            {/* Session Status */}
            <SessionStatusIndicator 
              status={session.status as 'draft' | 'active' | 'completed'}
              participantCount={participantCount}
            />

            {/* Instructions */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-3 text-purple-300">
                What happens next?
              </h3>
              <div className="space-y-3 text-gray-300">
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-purple-600/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-purple-400">1</span>
                  </div>
                  <div>
                    <p><strong>Stay on this page</strong> - You're all set! Keep this tab open.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-purple-600/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-purple-400">2</span>
                  </div>
                  <div>
                    <p><strong>Wait for the host</strong> - The session will start automatically.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-purple-600/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-purple-400">3</span>
                  </div>
                  <div>
                    <p><strong>Enjoy the activities</strong> - You'll be redirected when it begins!</p>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Right Column - Participants List */}
          <div className="lg:sticky lg:top-24 lg:self-start">
            <PreLobbyParticipantList sessionId={sessionId} />
          </div>

        </div>

        {/* Mobile-optimized bottom section */}
        <div className="mt-8 lg:hidden">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-4">
            <div className="text-center text-sm text-gray-400">
              <Clock className="w-4 h-4 inline-block mr-1" />
              This page updates automatically. Keep it open!
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default PreLobbyLandingPage;