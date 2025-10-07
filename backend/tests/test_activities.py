"""Tests for Activity operations and JSONB configuration."""
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Activity, ActivityStatus, Session, SessionStatus

pytestmark = pytest.mark.asyncio


class TestActivities:
    """Test cases for Activity JSONB configuration operations."""

    async def test_jsonb_query_on_config(self, db_session: AsyncSession):
        """Test JSONB queries on activity configuration."""
        # Create a session first
        session = Session(
            title="Test Session",
            description="Test description",
            qr_code="TEST1234",
            admin_code="ADMIN123",
            max_participants=10,
            status=SessionStatus.DRAFT,
        )
        db_session.add(session)
        await db_session.flush()  # Get the session ID

        # Create activity with specific config
        activity = Activity(
            session_id=session.id,
            type="planning_poker",
            config={
                "version": "1.0",
                "settings": {"timer": 300, "cards": [1, 2, 3, 5, 8]},
            },
            order_index=1,
            status=ActivityStatus.ACTIVE,
        )
        db_session.add(activity)
        await db_session.commit()

        # Query using JSONB operators
        result = await db_session.execute(
            text(
                """
                SELECT id, config FROM activities 
                WHERE config->>'version' = '1.0'
                AND config->'settings'->>'timer' = '300'
                AND session_id = :session_id
            """
            ),
            {"session_id": session.id},
        )

        row = result.first()
        assert row is not None
        assert row.config["version"] == "1.0"
        assert row.config["settings"]["timer"] == 300
