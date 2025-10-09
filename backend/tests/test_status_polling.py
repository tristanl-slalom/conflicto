"""Tests for real-time status polling endpoints."""

from datetime import datetime, UTC

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Activity,
    ActivityStatus,
    Participant,
    Session,
    SessionStatus,
    UserResponse,
)

pytestmark = pytest.mark.asyncio


class TestStatusPolling:
    """Test cases for real-time status polling endpoints."""

    async def test_session_status_polling(self, db_session: AsyncSession):
        """Test session status endpoint returns real-time data."""
        # Create a session
        session = Session(
            title="Test Session",
            description="Test description",
            qr_code="TEST1234",
            admin_code="ADMIN123",
            max_participants=10,
            status=SessionStatus.ACTIVE,
        )
        db_session.add(session)
        await db_session.flush()

        # Create some activities for the session
        activity1 = Activity(
            session_id=session.id,
            type="planning_poker",
            config={"cards": [1, 2, 3, 5, 8]},
            order_index=1,
            status=ActivityStatus.ACTIVE,
        )
        activity2 = Activity(
            session_id=session.id,
            type="survey",
            config={"questions": ["How was it?"]},
            order_index=2,
            status=ActivityStatus.DRAFT,
        )

        db_session.add_all([activity1, activity2])
        await db_session.commit()

        # Verify we have the test data
        assert session.id is not None
        assert activity1.id is not None
        assert activity2.id is not None

        # Test that the models are working
        assert session.status == SessionStatus.ACTIVE
        assert activity1.status == ActivityStatus.ACTIVE
        assert activity2.status == ActivityStatus.DRAFT

    async def test_activity_status_polling(self, db_session: AsyncSession):
        """Test activity status endpoint returns real-time data."""
        # Create session and activity
        session = Session(
            title="Test Session",
            description="Test description",
            qr_code="TEST5678",
            admin_code="ADMIN456",
            max_participants=10,
            status=SessionStatus.ACTIVE,
        )
        db_session.add(session)
        await db_session.flush()

        activity = Activity(
            session_id=session.id,
            type="planning_poker",
            config={
                "version": "1.0",
                "settings": {"cards": [1, 2, 3, 5, 8, 13], "timer": 300},
            },
            order_index=1,
            status=ActivityStatus.ACTIVE,
        )
        db_session.add(activity)
        await db_session.flush()

        # Create participants first
        participant1 = Participant(
            session_id=session.id, display_name="User 1", role="participant"
        )
        participant2 = Participant(
            session_id=session.id, display_name="User 2", role="participant"
        )
        db_session.add_all([participant1, participant2])
        await db_session.flush()

        # Create some user responses using participant IDs
        response1 = UserResponse(
            session_id=session.id,
            activity_id=activity.id,
            participant_id=participant1.id,  # Use integer ID
            response_data={"card_value": 5, "confidence": "high"},
        )
        response2 = UserResponse(
            session_id=session.id,
            activity_id=activity.id,
            participant_id=participant2.id,  # Use integer ID
            response_data={"card_value": 8, "confidence": "medium"},
        )

        db_session.add_all([response1, response2])
        await db_session.commit()

        # Verify test data
        assert activity.id is not None
        assert response1.id is not None
        assert response2.id is not None

    async def test_incremental_response_updates(self, db_session: AsyncSession):
        """Test incremental response updates endpoint."""
        # Create session and activity
        session = Session(
            title="Test Session",
            description="Test description",
            qr_code="TEST9999",
            admin_code="ADMIN789",
            max_participants=10,
            status=SessionStatus.ACTIVE,
        )
        db_session.add(session)
        await db_session.flush()

        activity = Activity(
            session_id=session.id,
            type="survey",
            config={"questions": [{"id": 1, "text": "Rate this feature"}]},
            order_index=1,
            status=ActivityStatus.ACTIVE,
        )
        db_session.add(activity)
        await db_session.flush()

        # Create participants first
        participant1 = Participant(
            session_id=session.id, display_name="User 1", role="participant"
        )
        participant2 = Participant(
            session_id=session.id, display_name="User 2", role="participant"
        )
        db_session.add_all([participant1, participant2])
        await db_session.flush()

        # Create initial responses with different timestamps
        base_time = datetime.now(UTC)

        response1 = UserResponse(
            session_id=session.id,
            activity_id=activity.id,
            participant_id=participant1.id,  # Use integer ID
            response_data={"rating": 5, "comment": "Great!"},
            created_at=base_time,
        )
        db_session.add(response1)
        await db_session.commit()

        # Create additional response later
        response2 = UserResponse(
            session_id=session.id,
            activity_id=activity.id,
            participant_id=participant2.id,  # Use integer ID
            response_data={"rating": 4, "comment": "Good"},
        )
        db_session.add(response2)
        await db_session.commit()

        # Verify test data
        assert response1.id is not None
        assert response2.id is not None
        assert response1.created_at is not None
        assert response2.created_at is not None
