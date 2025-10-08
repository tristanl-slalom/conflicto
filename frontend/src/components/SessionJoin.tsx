import React, { useState, useEffect } from 'react';
import { 
  useJoinSessionApiV1SessionsSessionIdJoinPost,
  useValidateNicknameApiV1SessionsSessionIdNicknamesValidateGet
} from '../api/generated';

interface SessionJoinProps {
  sessionId: string;
}

const SessionJoin: React.FC<SessionJoinProps> = ({ sessionId }) => {
  
  const [nickname, setNickname] = useState('');
  const [validationMessage, setValidationMessage] = useState('');

  // React Query hooks
  const joinSessionMutation = useJoinSessionApiV1SessionsSessionIdJoinPost();
  
  // Nickname validation query - only run when nickname is long enough
  const { 
    isLoading: isValidating,
    refetch: validateNickname 
  } = useValidateNicknameApiV1SessionsSessionIdNicknamesValidateGet(
    parseInt(sessionId),
    { nickname },
    {
      query: {
        enabled: false, // We'll trigger this manually
      }
    }
  );

  // Validate nickname as user types
  useEffect(() => {
    if (nickname.length < 2) {
      setValidationMessage('');
      return;
    }

    const timeoutId = setTimeout(async () => {
      try {
        const result = await validateNickname();
        const validation = result.data?.data;
        
        // Type guard to check if validation is successful and has the expected properties
        if (result.data?.status === 200 && validation && 'available' in validation) {
          if (validation.available) {
            setValidationMessage('✓ Nickname available');
          } else {
            setValidationMessage(
              ('suggested_nickname' in validation && validation.suggested_nickname)
                ? `❌ Taken. Try: ${validation.suggested_nickname}`
                : '❌ Nickname not available'
            );
          }
        } else {
          setValidationMessage('Unable to check nickname');
        }
      } catch (err) {
        setValidationMessage('Unable to check nickname');
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [nickname, validateNickname]);

  const handleJoinSession = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!nickname.trim() || nickname.length < 1) {
      return;
    }

    try {
      const result = await joinSessionMutation.mutateAsync({
        sessionId: parseInt(sessionId),
        data: { nickname: nickname.trim() }
      });
      
      const joinData = result.data;
      
      // Type guard to ensure we have a successful response
      if (result.status === 200 && 'participant_id' in joinData) {
        // Store participant data in sessionStorage for app use
        sessionStorage.setItem('participant_id', joinData.participant_id);
        sessionStorage.setItem('session_id', sessionId);
        sessionStorage.setItem('nickname', nickname.trim());
        
        // Log the session state for debugging
        console.log('Join successful:', joinData);
        if ('session_state' in joinData) {
          console.log('Session state:', joinData.session_state);
        }
        
        // Reload the page to trigger the route's logic to show the appropriate interface
        window.location.reload();
      } else {
        throw new Error('Failed to join session - unexpected response format');
      }
      
    } catch (err) {
      console.error('Join error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Join Session</h1>
          <p className="text-gray-600">Session ID: {sessionId}</p>
        </div>

        {/* Join Form */}
        <form onSubmit={handleJoinSession} className="space-y-6">
          <div>
            <label htmlFor="nickname" className="block text-sm font-medium text-gray-700 mb-2">
              Choose your nickname
            </label>
            <input
              id="nickname"
              type="text"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              placeholder="Enter your nickname"
              maxLength={50}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-lg"
              disabled={joinSessionMutation.isPending}
              autoFocus
            />
            
            {/* Validation Message */}
            {(validationMessage || isValidating) && (
              <div className="mt-2 text-sm">
                {isValidating ? (
                  <span className="text-gray-500">Checking availability...</span>
                ) : (
                  <span className={validationMessage.includes('✓') ? 'text-green-600' : 'text-orange-600'}>
                    {validationMessage}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Error Display */}
          {joinSessionMutation.error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-red-800 text-sm">
                  {('error' in joinSessionMutation.error && typeof joinSessionMutation.error.error === 'string') 
                    ? joinSessionMutation.error.error 
                    : 'Failed to join session'}
                </span>
              </div>
            </div>
          )}

          {/* Join Button */}
          <button
            type="submit"
            disabled={joinSessionMutation.isPending || !nickname.trim() || nickname.length < 1}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center"
          >
            {joinSessionMutation.isPending ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Joining...
              </>
            ) : (
              'Join Session'
            )}
          </button>
        </form>

        {/* Help Text */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Once you join, you'll be able to participate in session activities.</p>
          <p className="mt-1">Keep this page open during the session.</p>
        </div>
      </div>
    </div>
  );
};

export default SessionJoin;