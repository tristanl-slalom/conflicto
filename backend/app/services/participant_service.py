"""
Participant service for handling session joining, heartbeat, and management operations.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID

from sqlalchemy import and_, select, func, delete
from sqlalchemy.exc import IntegrityError

from app.db.models import Participant, Session as SessionModel, Activity
from app.models.schemas import (
    ParticipantJoinRequest,
    ParticipantJoinResponse,
    ParticipantHeartbeatRequest,
    ParticipantHeartbeatResponse,
    ParticipantStatus,
    NicknameValidationResponse,
)


class ParticipantService:
    """Service for managing participant operations."""

    # Status thresholds in seconds
    ONLINE_THRESHOLD = 30  # < 30s = online
    IDLE_THRESHOLD = 120  # 30s-2min = idle
    # > 2min = disconnected

    def __init__(self, db):
        self.db = db

    async def join_session(
        self, session_id: int, join_request: ParticipantJoinRequest
    ) -> ParticipantJoinResponse:
        """
        Join a participant to a session with nickname validation.

        Args:
            session_id: Session ID to join
            join_request: Participant join request with nickname

        Returns:
            ParticipantJoinResponse with participant_id and session state

        Raises:
            ValueError: If session not found or nickname taken
        """
        # Validate session exists
        result = await self.db.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError("Session not found")

        # Check if session allows new participants
        current_count = await self.get_participant_count(session_id)
        if current_count >= session.max_participants:
            raise ValueError("Session is full")

        # Validate nickname availability
        validation = await self.validate_nickname(session_id, join_request.nickname)
        if not validation.available:
            if validation.suggested_nickname:
                join_request.nickname = validation.suggested_nickname
            else:
                raise ValueError("Nickname not available and no alternatives found")

        # Create participant
        participant = Participant(
            session_id=session_id, nickname=join_request.nickname, connection_data={}
        )

        try:
            self.db.add(participant)
            await self.db.commit()
            await self.db.refresh(participant)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Nickname already taken")

        # Get current session state
        session_state = await self._get_session_state(session_id)

        return ParticipantJoinResponse(
            participant_id=str(participant.id), session_state=session_state
        )

    async def validate_nickname(
        self, session_id: int, nickname: str
    ) -> NicknameValidationResponse:
        """
        Validate if a nickname is available in a session.

        Args:
            session_id: Session to check nickname in
            nickname: Desired nickname

        Returns:
            NicknameValidationResponse with availability and suggested alternatives
        """
        # Check if nickname is already taken
        result = await self.db.execute(
            select(Participant).where(
                and_(
                    Participant.session_id == session_id,
                    Participant.nickname == nickname,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if not existing:
            return NicknameValidationResponse(available=True)

        # Generate suggested alternatives
        suggested = await self._generate_nickname_suggestion(session_id, nickname)

        return NicknameValidationResponse(available=False, suggested_nickname=suggested)

    async def update_heartbeat(
        self, participant_id: UUID, heartbeat_request: ParticipantHeartbeatRequest
    ) -> ParticipantHeartbeatResponse:
        """
        Update participant heartbeat and return current activity context.

        Args:
            participant_id: UUID of participant
            heartbeat_request: Heartbeat data including activity context

        Returns:
            ParticipantHeartbeatResponse with status and activity context

        Raises:
            ValueError: If participant not found
        """
        result = await self.db.execute(
            select(Participant).where(Participant.id == participant_id)
        )
        participant = result.scalar_one_or_none()
        if not participant:
            raise ValueError("Participant not found")

        # Update last_seen and connection_data
        participant.last_seen = datetime.now(timezone.utc)
        if heartbeat_request.activity_context:
            participant.connection_data = heartbeat_request.activity_context

        await self.db.commit()

        # Compute status based on last_seen
        status = self._compute_participant_status(participant.last_seen)

        # Get current activity context for session
        activity_context = await self._get_activity_context(participant.session_id)

        return ParticipantHeartbeatResponse(
            status=status,
            activity_context=activity_context,
            updated_at=participant.last_seen,
        )

    async def get_session_participants(
        self, session_id: int
    ) -> List[ParticipantStatus]:
        """
        Get all participants for a session with computed status.

        Args:
            session_id: Session ID to get participants for

        Returns:
            List of ParticipantStatus with computed online/idle/disconnected status
        """
        result = await self.db.execute(
            select(Participant).where(Participant.session_id == session_id)
        )
        participants = result.scalars().all()

        participant_statuses = []
        for p in participants:
            status = self._compute_participant_status(p.last_seen)
            participant_statuses.append(
                ParticipantStatus(
                    participant_id=str(p.id),
                    nickname=p.nickname,
                    status=status,
                    joined_at=p.joined_at,
                    last_seen=p.last_seen,
                )
            )

        return participant_statuses

    async def remove_participant(self, participant_id: UUID) -> bool:
        """
        Remove a participant from their session.

        Args:
            participant_id: UUID of participant to remove

        Returns:
            True if removed successfully
        """
        # Use explicit DELETE statement for async session

        result = await self.db.execute(
            delete(Participant).where(Participant.id == participant_id)
        )

        if result.rowcount == 0:
            return False

        await self.db.commit()
        return True

    async def get_participant_count(self, session_id: int) -> int:
        """Get current participant count for a session."""
        result = await self.db.execute(
            select(func.count(Participant.id)).where(
                Participant.session_id == session_id
            )
        )
        return result.scalar()

    def _compute_participant_status(self, last_seen: datetime) -> str:
        """
        Compute participant status based on last_seen timestamp.

        Args:
            last_seen: When participant was last seen

        Returns:
            Status string: "online", "idle", or "disconnected"
        """
        now = datetime.now(timezone.utc)
        # Ensure last_seen has timezone info
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        seconds_since_seen = (now - last_seen).total_seconds()

        if seconds_since_seen < self.ONLINE_THRESHOLD:
            return "online"
        elif seconds_since_seen < self.IDLE_THRESHOLD:
            return "idle"
        else:
            return "disconnected"

    async def _get_session_state(self, session_id: int) -> Dict[str, Any]:
        """
        Get current session state including active activity and configuration.

        Args:
            session_id: Session ID to get state for

        Returns:
            Dictionary with current session state
        """
        result = await self.db.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return {}

        # Get current active activity
        activity_result = await self.db.execute(
            select(Activity).where(
                and_(Activity.session_id == session_id, Activity.status == "active")
            )
        )
        current_activity = activity_result.scalar_one_or_none()

        participant_count = await self.get_participant_count(session_id)

        return {
            "session_id": session_id,
            "session_title": session.title,
            "session_status": session.status,
            "current_activity": (
                {
                    "id": str(current_activity.id) if current_activity else None,
                    "type": current_activity.type if current_activity else None,
                    "config": current_activity.config if current_activity else None,
                }
                if current_activity
                else None
            ),
            "participant_count": participant_count,
        }

    async def _get_activity_context(self, session_id: int) -> Dict[str, Any]:
        """
        Get current activity context for heartbeat responses.

        Args:
            session_id: Session ID to get activity context for

        Returns:
            Dictionary with current activity context
        """
        result = await self.db.execute(
            select(Activity).where(
                and_(Activity.session_id == session_id, Activity.status == "active")
            )
        )
        current_activity = result.scalar_one_or_none()

        if not current_activity:
            return {"message": "No active activity"}

        return {
            "activity_id": str(current_activity.id),
            "activity_type": current_activity.type,
            "config": current_activity.config,
            "instructions": current_activity.config.get("instructions", ""),
            "status": current_activity.status,
        }

    async def _generate_nickname_suggestion(
        self, session_id: int, base_nickname: str
    ) -> Optional[str]:
        """
        Generate a suggested nickname when the desired one is taken.

        Args:
            session_id: Session ID to check uniqueness in
            base_nickname: Base nickname to modify

        Returns:
            Suggested unique nickname or None if no alternatives found
        """
        # Try appending numbers 1-99
        for i in range(1, 100):
            suggested = f"{base_nickname}{i}"
            if len(suggested) <= 50:  # Respect max length
                result = await self.db.execute(
                    select(Participant).where(
                        and_(
                            Participant.session_id == session_id,
                            Participant.nickname == suggested,
                        )
                    )
                )
                existing = result.scalar_one_or_none()

                if not existing:
                    return suggested

        return None
