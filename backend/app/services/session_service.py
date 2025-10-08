"""
Session service layer for business logic.
"""
import secrets
import string
from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.db.models import Activity, Participant, Session
from app.db.enums import SessionStatus
from app.models.schemas import SessionCreate, SessionUpdate

logger = get_logger(__name__)


class SessionService:
    """Service class for session operations."""

    @staticmethod
    def _generate_code(length: int = 6) -> str:
        """Generate a random alphanumeric code."""
        alphabet = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    async def create_session(db: AsyncSession, session_data: SessionCreate) -> Session:
        """Create a new session."""
        logger.info("Creating new session", title=session_data.title)

        # Generate unique codes
        qr_code = SessionService._generate_code(8)
        admin_code = SessionService._generate_code(6)

        # Ensure uniqueness (simplified for MVP)
        while await SessionService._code_exists(db, qr_code=qr_code):
            qr_code = SessionService._generate_code(8)

        while await SessionService._code_exists(db, admin_code=admin_code):
            admin_code = SessionService._generate_code(6)

        session = Session(
            title=session_data.title,
            description=session_data.description,
            max_participants=session_data.max_participants,
            qr_code=qr_code,
            admin_code=admin_code,
            status=SessionStatus.DRAFT,
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        logger.info("Session created", session_id=session.id, qr_code=qr_code)
        return session

    @staticmethod
    async def get_session(
        db: AsyncSession, session_id: int, include_relations: bool = False
    ) -> Optional[Session]:
        """Get a session by ID."""
        query = select(Session).where(Session.id == session_id)

        if include_relations:
            query = query.options(
                selectinload(Session.activities), selectinload(Session.participants)
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_session_by_code(
        db: AsyncSession, code: str, code_type: str = "qr"
    ) -> Optional[Session]:
        """Get a session by QR code or admin code."""
        if code_type == "qr":
            query = select(Session).where(Session.qr_code == code)
        elif code_type == "admin":
            query = select(Session).where(Session.admin_code == code)
        else:
            return None

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_sessions(
        db: AsyncSession, offset: int = 0, limit: int = 100
    ) -> list[Session]:
        """List sessions with pagination."""
        query = (
            select(Session)
            .offset(offset)
            .limit(limit)
            .order_by(Session.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_session(
        db: AsyncSession, session_id: int, session_data: SessionUpdate
    ) -> Optional[Session]:
        """Update a session."""
        session = await SessionService.get_session(db, session_id)
        if not session:
            return None

        logger.info("Updating session", session_id=session_id)

        # Update fields
        if session_data.title is not None:
            session.title = session_data.title
        if session_data.description is not None:
            session.description = session_data.description
        if session_data.max_participants is not None:
            session.max_participants = session_data.max_participants
        if session_data.status is not None:
            old_status = session.status
            session.status = session_data.status

            # Handle status transitions
            if (
                old_status == SessionStatus.DRAFT
                and session.status == SessionStatus.ACTIVE
            ):
                session.started_at = datetime.utcnow()
            elif (
                session.status == SessionStatus.COMPLETED
                and session.completed_at is None
            ):
                session.completed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(session)

        logger.info("Session updated", session_id=session_id, status=session.status)
        return session

    @staticmethod
    async def delete_session(db: AsyncSession, session_id: int) -> bool:
        """Delete a session."""
        session = await SessionService.get_session(db, session_id)
        if not session:
            return False

        logger.info("Deleting session", session_id=session_id)
        await db.delete(session)
        await db.commit()
        return True

    @staticmethod
    async def get_session_stats(db: AsyncSession, session_id: int) -> dict:
        """Get session statistics."""
        session = await SessionService.get_session(db, session_id)
        if not session:
            return {}

        # Count participants
        participant_count = await db.execute(
            select(func.count(Participant.id)).where(
                Participant.session_id == session_id
            )
        )

        # Count activities
        activity_count = await db.execute(
            select(func.count(Activity.id)).where(Activity.session_id == session_id)
        )

        return {
            "participant_count": participant_count.scalar() or 0,
            "activity_count": activity_count.scalar() or 0,
            "status": session.status,
            "created_at": session.created_at,
        }

    @staticmethod
    async def _code_exists(
        db: AsyncSession, qr_code: str | None = None, admin_code: str | None = None
    ) -> bool:
        """Check if a code already exists."""
        if qr_code:
            result = await db.execute(select(Session).where(Session.qr_code == qr_code))
            return result.scalar_one_or_none() is not None

        if admin_code:
            result = await db.execute(
                select(Session).where(Session.admin_code == admin_code)
            )
            return result.scalar_one_or_none() is not None

        return False
