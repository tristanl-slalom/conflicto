import { createFileRoute } from '@tanstack/react-router'
import SessionJoin from '../../components/SessionJoin'

export const Route = createFileRoute('/join/$sessionId')({
  component: SessionJoinPage,
})

function SessionJoinPage() {
  const { sessionId } = Route.useParams()
  return <SessionJoin sessionId={sessionId} />
}