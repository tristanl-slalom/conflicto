/**
 * Example component demonstrating Orval-generated API hooks
 *
 * This demonstrates how to use the automatically generated TypeScript
 * API client hooks from the OpenAPI specification.
 */

import {
  useListSessionsApiV1SessionsGet,
  useCreateSessionApiV1SessionsPost,
  type SessionCreate,
} from '../api/generated';

export function SessionsExample() {
  // Query hook - automatically provides loading states, error handling, caching
  const {
    data: sessionsData,
    isLoading,
    error,
  } = useListSessionsApiV1SessionsGet();

  // Mutation hook - for creating new sessions
  const createSessionMutation = useCreateSessionApiV1SessionsPost();

  const handleCreateSession = async () => {
    const newSession: SessionCreate = {
      title: 'Example Session',
      description: 'Created using Orval-generated hooks',
      max_participants: 50,
    };

    try {
      const result = await createSessionMutation.mutateAsync({
        data: newSession,
      });
      console.log('Session created:', result.data);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  if (isLoading) {
    return <div>Loading sessions...</div>;
  }

  if (error) {
    return <div>Error loading sessions: {error.message}</div>;
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Sessions (Orval Example)</h2>
      <button
        onClick={handleCreateSession}
        disabled={createSessionMutation.isPending}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {createSessionMutation.isPending
          ? 'Creating...'
          : 'Create Example Session'}
      </button>

      <div className="space-y-2">
        <p>Total Sessions: {sessionsData?.data.total || 0}</p>

        {sessionsData?.data.sessions.map(session => (
          <div key={session.id} className="p-3 border rounded">
            <h3 className="font-semibold">{session.title}</h3>
            <p className="text-gray-600">{session.description}</p>
            <div className="text-sm text-gray-500">
              Status: {session.status} | Max Participants:{' '}
              {session.max_participants}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
