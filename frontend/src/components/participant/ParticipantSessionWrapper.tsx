import React from 'react';
import { useSessionTransition } from '../../hooks/useSessionStatus';
import PreLobbyLandingPage from '../lobby/PreLobbyLandingPage';

interface ParticipantSessionWrapperProps {
  sessionId: number;
  children: React.ReactNode;
  nickname?: string;
}

/**
 * Wrapper component that handles session status-based routing
 * Shows pre-lobby for draft sessions, regular content for active sessions
 */
const ParticipantSessionWrapper: React.FC<ParticipantSessionWrapperProps> = ({
  sessionId,
  children,
  nickname
}) => {
  const sessionStatus = useSessionTransition(
    sessionId,
    (newStatus: string, previousStatus: string | null) => {
      console.log(`Session status transition: ${previousStatus} → ${newStatus}`);
      
      // Handle specific transitions
      if (previousStatus === 'draft' && newStatus === 'active') {
        console.log('Session has started! Transitioning to active view...');
        // The component will re-render automatically due to status change
      }
    }
  );

  // Handle loading state
  if (sessionStatus.isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <div className="text-lg font-medium">Loading session...</div>
          <div className="text-sm text-gray-400 mt-2">Checking session status</div>
        </div>
      </div>
    );
  }

  // Handle error state
  if (sessionStatus.error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold mb-4">Session Not Found</h1>
          <p className="text-gray-300 mb-6">
            The session you're trying to join could not be found or may have been removed.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => {
                // Clear any cached session data and go home instead of refreshing
                sessionStorage.clear();
                window.location.href = '/';
              }}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Go Home
            </button>
            <button
              onClick={() => {
                // Only reload if user explicitly wants to try again
                window.location.reload();
              }}
              className="w-full bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Handle different session statuses
  switch (sessionStatus.status) {
    case 'draft':
      // For draft sessions, check if user has joined
      if (nickname) {
        // User has joined - show pre-lobby
        return (
          <PreLobbyLandingPage 
            sessionId={sessionId}
            nickname={nickname}
          />
        );
      } else {
        // User hasn't joined yet - show join form
        return <>{children}</>;
      }
      
    case 'active':
      // Show regular participant interface for active sessions
      return <>{children}</>;
      
    case 'completed':
      // Show completion message for completed sessions
      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
          <div className="text-center max-w-md mx-auto p-6">
            <div className="text-green-400 text-6xl mb-4">✅</div>
            <h1 className="text-2xl font-bold mb-4">Session Completed</h1>
            <p className="text-gray-300 mb-6">
              Thank you for participating in "{sessionStatus.title}". 
              The session has ended.
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Return Home
            </button>
          </div>
        </div>
      );
      
    default:
      // Unknown status - show error state
      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
          <div className="text-center max-w-md mx-auto p-6">
            <div className="text-gray-400 text-6xl mb-4">❓</div>
            <h1 className="text-2xl font-bold mb-4">Unknown Session Status</h1>
            <p className="text-gray-300 mb-6">
              The session status could not be determined. Please try refreshing the page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
  }
};

export default ParticipantSessionWrapper;