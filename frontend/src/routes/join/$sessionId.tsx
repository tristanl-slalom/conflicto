import { createFileRoute } from '@tanstack/react-router'
import SessionJoin from '../../components/SessionJoin'
import ParticipantSessionWrapper from '../../components/participant/ParticipantSessionWrapper'

export const Route = createFileRoute('/join/$sessionId')({
  component: SessionJoinPage,
})

function SessionJoinPage() {
  const { sessionId } = Route.useParams()
  
  // Check if user has already joined (has participant_id in storage)
  const participantId = sessionStorage.getItem('participant_id')
  const storedSessionId = sessionStorage.getItem('session_id')
  const nickname = sessionStorage.getItem('nickname')
  
  // If user has already joined this session, show the appropriate interface
  if (participantId && storedSessionId === sessionId && nickname) {
    return (
      <ParticipantSessionWrapper 
        sessionId={parseInt(sessionId)}
        nickname={nickname}
      >
        {/* This will be the active session participant interface */}
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Active Session Interface</h1>
            <p className="text-gray-300">
              Welcome back, {nickname}! Session activities would appear here.
            </p>
          </div>
        </div>
      </ParticipantSessionWrapper>
    )
  }
  
  // If not joined yet, show the join form
  return <SessionJoin sessionId={sessionId} />
}