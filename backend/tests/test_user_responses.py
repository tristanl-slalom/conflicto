"""Test cases for User Response functionality including JSONB operations."""

from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Activity, Participant, Session, UserResponse


class TestUserResponses:
    """Test JSONB functionality for user responses."""

    async def test_create_user_response_with_jsonb(self, db_session: AsyncSession):
        """Test creating a user response with JSONB data."""
        # Create required entities first
        session = Session(
            title="Test Session",
            description="Test session for user responses",
            status="active",
            qr_code="TEST123",
            admin_code="ADMIN123",
        )
        db_session.add(session)
        await db_session.flush()

        activity = Activity(
            session_id=session.id,
            type="poll",
            status="active",
            config={
                "type": "poll",
                "version": "1.0",
                "data": {
                    "question": "What is your favorite color?",
                    "options": ["red", "blue", "green", "yellow"],
                },
            },
            order_index=1,
        )
        db_session.add(activity)
        await db_session.flush()

        participant = Participant(
            session_id=session.id, display_name="Test Participant"
        )
        db_session.add(participant)
        await db_session.flush()

        # Create user response with JSONB data
        response_data = {
            "type": "poll",
            "version": "1.0",
            "data": {"choice": "blue"},
            "metadata": {"timestamp": "2025-10-07T16:30:00Z"},
        }

        user_response = UserResponse(
            session_id=session.id,
            activity_id=activity.id,
            participant_id=participant.id,
            response_data=response_data,
        )
        db_session.add(user_response)
        await db_session.commit()

        # Verify the response was created correctly
        assert user_response.id is not None
        assert user_response.response_data["type"] == "poll"
        assert user_response.response_data["data"]["choice"] == "blue"

    async def test_query_jsonb_data(self, db_session: AsyncSession):
        """Test querying JSONB data using PostgreSQL operators."""
        # Create test data
        session = Session(
            title="JSONB Query Test",
            description="Testing JSONB queries",
            status="active",
            qr_code="JSONB123",
            admin_code="ADMIN456",
        )
        db_session.add(session)
        await db_session.flush()

        activity = Activity(
            session_id=session.id,
            type="planning_poker",
            status="active",
            config={"type": "planning_poker", "version": "1.0"},
            order_index=1,
        )
        db_session.add(activity)
        await db_session.flush()

        participant = Participant(
            session_id=session.id, display_name="Query Test Participant"
        )
        db_session.add(participant)
        await db_session.flush()

        # Create multiple responses with different JSONB data
        responses_data = [
            {"type": "planning_poker", "data": {"estimate": 5}},
            {"type": "planning_poker", "data": {"estimate": 8}},
            {"type": "poll", "data": {"choice": "option_a"}},
        ]

        for data in responses_data:
            response = UserResponse(
                session_id=session.id,
                activity_id=activity.id,
                participant_id=participant.id,
                response_data=data,
            )
            db_session.add(response)

        await db_session.commit()

        # Query for planning poker responses
        from sqlalchemy import text

        query = text(
            """
            SELECT COUNT(*) FROM user_responses 
            WHERE response_data @> '{"type": "planning_poker"}'
        """
        )
        result = await db_session.execute(query)
        count = result.scalar()
        assert count == 2


class TestUserResponsePerformance:
    """Test performance aspects of JSONB operations."""

    async def test_jsonb_aggregation(self, db_session: AsyncSession):
        """Test JSONB aggregation operations."""
        # Create test session, activity, and participant
        session = Session(
            title="Aggregation Test",
            description="Testing JSONB aggregations",
            status="active",
            qr_code="AGG123",
            admin_code="ADMIN789",
        )
        db_session.add(session)
        await db_session.flush()

        activity = Activity(
            session_id=session.id,
            type="planning_poker",
            status="active",
            config={"type": "planning_poker", "version": "1.0"},
            order_index=1,
        )
        db_session.add(activity)
        await db_session.flush()

        participant = Participant(
            session_id=session.id, display_name="Aggregation Participant"
        )
        db_session.add(participant)
        await db_session.flush()

        # Create responses with estimates
        estimates = [1, 2, 3, 5, 8, 13, 5, 8, 3, 5]
        for estimate in estimates:
            user_response = UserResponse(
                session_id=session.id,
                activity_id=activity.id,
                participant_id=participant.id,
                response_data={
                    "type": "planning_poker",
                    "version": "1.0",
                    "data": {"estimate": estimate},
                },
            )
            db_session.add(user_response)

        await db_session.commit()

        # Test aggregation query
        from sqlalchemy import text

        query = text(
            """
            SELECT 
                (response_data->'data'->>'estimate')::int as estimate,
                COUNT(*) as count
            FROM user_responses 
            WHERE session_id = :session_id
            AND response_data @> '{"type": "planning_poker"}'
            GROUP BY response_data->'data'->>'estimate'
            ORDER BY estimate
        """
        )

        result = await db_session.execute(query, {"session_id": session.id})
        results = result.fetchall()

        # Verify aggregation results
        estimate_counts = {row[0]: row[1] for row in results}
        assert estimate_counts[5] == 3  # 5 appears 3 times
        assert estimate_counts[8] == 2  # 8 appears 2 times

    @pytest.mark.skip(
        reason="GIN indexes are created by migrations, not available in test environment using Base.metadata.create_all()"
    )
    async def test_gin_index_performance(self, db_session: AsyncSession):
        """Test GIN index performance for JSONB operations."""
        # This test would verify that GIN indexes are being used
        # In a real environment with proper migrations
        pass
