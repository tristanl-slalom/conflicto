"""
Comprehensive tests for UserResponseService to improve test coverage.
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4, UUID

from app.services.user_response_service import UserResponseService
from app.models.jsonb_schemas.user_response import UserResponseCreate, UserResponseUpdate
from app.db.models import UserResponse


class TestUserResponseService:
    """Test UserResponseService methods to improve coverage."""

    @pytest.fixture
    async def sample_user_response_data(self):
        """Sample user response data for testing."""
        return UserResponseCreate(
            response_data={
                "question": "What's your favorite programming language?",
                "answer": "Python",
                "confidence": 0.95,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    @pytest.fixture
    async def sample_session_activity_participant(self, db_session):
        """Create sample session, activity, and participant for testing."""
        from app.services.session_service import SessionService
        from app.services.activity_service import ActivityService
        from app.models.schemas import SessionCreate
        from app.models.jsonb_schemas.activity import ActivityCreate
        from app.db.models import Participant
        from app.db.enums import ParticipantRole
        
        # Create session
        session_data = SessionCreate(
            title="Test Session for User Responses",
            description="Testing user responses"
        )
        session = await SessionService.create_session(db_session, session_data)
        
        # Create activity
        activity_data = ActivityCreate(
            type="poll",
            config={"question": "Test question?", "options": ["A", "B", "C"]},
            order_index=1
        )
        activity = await ActivityService.create_activity(
            db_session, session.id, activity_data
        )
        
        # Create participant
        participant = Participant(
            session_id=session.id,
            display_name="Test User",
            role=ParticipantRole.PARTICIPANT
        )
        db_session.add(participant)
        await db_session.commit()
        await db_session.refresh(participant)
        
        return {
            "session_id": session.id,
            "activity_id": activity.id,
            "participant_id": participant.id
        }

    async def test_create_response(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test creating a user response."""
        data = sample_session_activity_participant
        
        response = await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"],
            response_data=sample_user_response_data
        )
        
        assert response.session_id == data["session_id"]
        assert response.activity_id == data["activity_id"]
        assert response.participant_id == data["participant_id"]
        assert response.response_data["answer"] == "Python"
        assert response.id is not None
        assert response.created_at is not None

    async def test_get_activity_responses(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test getting all responses for an activity."""
        data = sample_session_activity_participant
        
        # Create multiple responses
        response1 = await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"],
            response_data=sample_user_response_data
        )
        
        # Create another response data
        response_data2 = UserResponseCreate(
            response_data={"answer": "JavaScript", "confidence": 0.8}
        )
        response2 = await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"],
            response_data=response_data2
        )
        
        # Get all responses
        responses = await UserResponseService.get_activity_responses(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"]
        )
        
        assert len(responses) == 2
        # Check that both responses are present (order might vary slightly due to timing)
        response_ids = [r.id for r in responses]
        assert response1.id in response_ids
        assert response2.id in response_ids

    async def test_get_activity_responses_with_pagination(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test getting activity responses with pagination."""
        data = sample_session_activity_participant
        
        # Create 3 responses
        for i in range(3):
            response_data = UserResponseCreate(
                response_data={"answer": f"Answer {i}", "index": i}
            )
            await UserResponseService.create_response(
                db=db_session,
                session_id=data["session_id"],
                activity_id=data["activity_id"],
                participant_id=data["participant_id"],
                response_data=response_data
            )
        
        # Test pagination
        responses_page1 = await UserResponseService.get_activity_responses(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            offset=0,
            limit=2
        )
        
        responses_page2 = await UserResponseService.get_activity_responses(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            offset=2,
            limit=2
        )
        
        assert len(responses_page1) == 2
        assert len(responses_page2) == 1

    async def test_get_participant_response(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test getting a specific participant's response."""
        data = sample_session_activity_participant
        
        # Create response
        created_response = await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"],
            response_data=sample_user_response_data
        )
        
        # Get participant response
        response = await UserResponseService.get_participant_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"]
        )
        
        assert response is not None
        assert response.id == created_response.id
        assert response.participant_id == data["participant_id"]

    async def test_get_participant_response_not_found(self, db_session, sample_session_activity_participant):
        """Test getting participant response when none exists."""
        data = sample_session_activity_participant
        
        response = await UserResponseService.get_participant_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=999  # Non-existent participant
        )
        
        assert response is None

    async def test_update_response(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test updating an existing response."""
        data = sample_session_activity_participant
        
        # Create response
        response = await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"],
            response_data=sample_user_response_data
        )
        
        # Update response
        update_data = UserResponseUpdate(
            response_data={
                "question": "What's your favorite programming language?",
                "answer": "TypeScript",  # Changed answer
                "confidence": 0.85,
                "updated": True
            }
        )
        
        updated_response = await UserResponseService.update_response(
            db=db_session,
            response_id=response.id,
            response_data=update_data
        )
        
        assert updated_response is not None
        assert updated_response.id == response.id
        assert updated_response.response_data["answer"] == "TypeScript"
        assert updated_response.response_data["updated"] is True

    async def test_update_response_not_found(self, db_session):
        """Test updating a non-existent response."""
        update_data = UserResponseUpdate(
            response_data={"answer": "Updated answer"}
        )
        
        result = await UserResponseService.update_response(
            db=db_session,
            response_id=uuid4(),  # Random UUID
            response_data=update_data
        )
        
        assert result is None

    async def test_delete_response(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test deleting a response."""
        data = sample_session_activity_participant
        
        # Create response
        response = await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"],
            response_data=sample_user_response_data
        )
        
        # Delete response
        deleted = await UserResponseService.delete_response(
            db=db_session,
            response_id=response.id
        )
        
        assert deleted is True
        
        # Verify it's deleted
        found_response = await UserResponseService.get_participant_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"]
        )
        assert found_response is None

    async def test_delete_response_not_found(self, db_session):
        """Test deleting a non-existent response."""
        result = await UserResponseService.delete_response(
            db=db_session,
            response_id=uuid4()  # Random UUID
        )
        
        assert result is False

    async def test_get_response_summary(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test getting response summary statistics."""
        data = sample_session_activity_participant
        
        # Create multiple responses from different participants
        # First response
        await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"],
            response_data=sample_user_response_data
        )
        
        # Create another participant and response
        from app.db.models import Participant
        from app.db.enums import ParticipantRole
        participant2 = Participant(
            session_id=data["session_id"],
            display_name="Test User 2",
            role=ParticipantRole.PARTICIPANT
        )
        db_session.add(participant2)
        await db_session.commit()
        await db_session.refresh(participant2)
        
        response_data2 = UserResponseCreate(
            response_data={"answer": "Java", "confidence": 0.7}
        )
        await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=participant2.id,
            response_data=response_data2
        )
        
        # Get summary
        summary = await UserResponseService.get_response_summary(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"]
        )
        
        assert summary["total_responses"] == 2
        assert summary["unique_participants"] == 2
        assert summary["last_updated"] is not None

    async def test_get_response_summary_empty(self, db_session, sample_session_activity_participant):
        """Test getting summary for activity with no responses."""
        data = sample_session_activity_participant
        
        summary = await UserResponseService.get_response_summary(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"]
        )
        
        assert summary["total_responses"] == 0
        assert summary["unique_participants"] == 0
        assert summary["last_updated"] is None

    async def test_get_responses_by_participant(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test getting all responses by a specific participant."""
        data = sample_session_activity_participant
        
        # Create multiple responses for the participant
        response1 = await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"],
            response_data=sample_user_response_data
        )
        
        # Create another activity and response for same participant
        from app.services.activity_service import ActivityService
        from app.models.jsonb_schemas.activity import ActivityCreate
        
        activity_data = ActivityCreate(
            type="survey",
            config={"question": "Another question?"},
            order_index=2
        )
        activity2 = await ActivityService.create_activity(
            db_session, data["session_id"], activity_data
        )
        
        response_data2 = UserResponseCreate(
            response_data={"answer": "Survey answer", "rating": 5}
        )
        response2 = await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=activity2.id,
            participant_id=data["participant_id"],
            response_data=response_data2
        )
        
        # Get responses by participant
        responses = await UserResponseService.get_responses_by_participant(
            db=db_session,
            session_id=data["session_id"],
            participant_id=data["participant_id"]
        )
        
        assert len(responses) == 2
        response_ids = [r.id for r in responses]
        assert response1.id in response_ids
        assert response2.id in response_ids

    async def test_get_responses_by_participant_with_pagination(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test getting participant responses with pagination."""
        data = sample_session_activity_participant
        
        # Create multiple activities and responses
        from app.services.activity_service import ActivityService
        from app.models.jsonb_schemas.activity import ActivityCreate
        
        for i in range(3):
            activity_data = ActivityCreate(
                type=f"poll_{i}",
                config={"question": f"Question {i}?"},
                order_index=i
            )
            activity = await ActivityService.create_activity(
                db_session, data["session_id"], activity_data
            )
            
            response_data = UserResponseCreate(
                response_data={"answer": f"Answer {i}", "index": i}
            )
            await UserResponseService.create_response(
                db=db_session,
                session_id=data["session_id"],
                activity_id=activity.id,
                participant_id=data["participant_id"],
                response_data=response_data
            )
        
        # Test pagination
        responses_page1 = await UserResponseService.get_responses_by_participant(
            db=db_session,
            session_id=data["session_id"],
            participant_id=data["participant_id"],
            offset=0,
            limit=2
        )
        
        responses_page2 = await UserResponseService.get_responses_by_participant(
            db=db_session,
            session_id=data["session_id"],
            participant_id=data["participant_id"],
            offset=2,
            limit=2
        )
        
        assert len(responses_page1) == 2
        assert len(responses_page2) == 1

    async def test_get_responses_since(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test getting responses created since a specific timestamp."""
        data = sample_session_activity_participant
        
        # Create a response first
        response = await UserResponseService.create_response(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            participant_id=data["participant_id"],
            response_data=sample_user_response_data
        )
        
        # Use a timestamp that's definitely before the response
        since_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
        
        # Get responses since the timestamp
        result = await UserResponseService.get_responses_since(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            since=since_time
        )
        
        assert result["count"] == 1
        assert result["since"] == since_time
        assert len(result["items"]) == 1
        assert result["items"][0].id == response.id

    async def test_get_responses_since_empty(self, db_session, sample_session_activity_participant):
        """Test getting responses since timestamp when none exist."""
        data = sample_session_activity_participant
        
        # Use current time - should find no responses
        since_time = datetime.now(timezone.utc)
        
        result = await UserResponseService.get_responses_since(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            since=since_time
        )
        
        assert result["count"] == 0
        assert result["since"] == since_time
        assert len(result["items"]) == 0

    async def test_get_responses_since_with_limit(self, db_session, sample_session_activity_participant, sample_user_response_data):
        """Test getting responses since timestamp with limit."""
        data = sample_session_activity_participant
        
        # Use a timestamp that's definitely before any responses are created
        since_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
        
        # Create multiple responses
        for i in range(3):
            response_data = UserResponseCreate(
                response_data={"answer": f"Answer {i}", "index": i}
            )
            await UserResponseService.create_response(
                db=db_session,
                session_id=data["session_id"],
                activity_id=data["activity_id"],
                participant_id=data["participant_id"],
                response_data=response_data
            )
        
        # Get responses with limit
        result = await UserResponseService.get_responses_since(
            db=db_session,
            session_id=data["session_id"],
            activity_id=data["activity_id"],
            since=since_time,
            limit=2
        )
        
        assert result["count"] == 2  # Limited to 2
        assert len(result["items"]) == 2