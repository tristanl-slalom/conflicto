"""
Tests for Activity API routes and services.
"""
import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import ActivityStatus
from app.models.jsonb_schemas.activity import ActivityCreate, ActivityUpdate
from app.services.activity_service import ActivityService


class TestActivityAPI:
    """Test Activity API endpoints."""
    
    @pytest.fixture
    async def sample_session(self, db_session: AsyncSession):
        """Create a sample session for testing."""
        from app.services.session_service import SessionService
        from app.models.schemas import SessionCreate
        
        session_data = SessionCreate(
            title="Test Session for Activities",
            description="A session for testing activities", 
            max_participants=50
        )
        session = await SessionService.create_session(db_session, session_data)
        
        # Return as dict to match API response format
        return {
            "id": session.id,
            "title": session.title,
            "description": session.description,
            "max_participants": session.max_participants,
            "status": session.status.value if hasattr(session.status, 'value') else session.status
        }

    @pytest.fixture
    def sample_activity_data(self):
        """Sample activity data for testing."""
        return {
            "type": "poll", 
            "config": {
                "question": "What's your favorite color?",
                "options": ["Red", "Blue", "Green", "Yellow"],
                "multiple_choice": False
            },
            "order_index": 1,
            "status": "draft"  # String for JSON API
        }

    async def test_create_activity(self, async_client: AsyncClient, sample_session, sample_activity_data):
        """Test creating an activity."""
        activity_data = sample_activity_data.copy()
        activity_data["session_id"] = sample_session["id"]
        
        response = await async_client.post(
            f"/api/v1/sessions/{sample_session['id']}/activities",
            json=activity_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == activity_data["type"]
        assert data["config"] == activity_data["config"]
        assert data["order_index"] == activity_data["order_index"]
        assert data["status"] == activity_data["status"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["session_id"] == sample_session["id"]

    async def test_create_activity_invalid_session(self, async_client: AsyncClient, sample_activity_data):
        """Test creating activity for non-existent session."""
        response = await async_client.post(
            "/api/v1/sessions/99999/activities", 
            json=sample_activity_data
        )
        assert response.status_code == 400

    async def test_get_session_activities(self, async_client: AsyncClient, sample_session):
        """Test getting all activities for a session."""
        session_id = sample_session["id"]
        
        # Create multiple activities
        activity1_data = {
            "type": "poll",
            "config": {"question": "Question 1?"},
            "order_index": 1,
            "status": "active"
        }
        activity2_data = {
            "type": "word_cloud", 
            "config": {"prompt": "Enter words"},
            "order_index": 2,
            "status": "draft"
        }
        
        await async_client.post(f"/api/v1/sessions/{session_id}/activities", json=activity1_data)
        await async_client.post(f"/api/v1/sessions/{session_id}/activities", json=activity2_data)
        
        response = await async_client.get(f"/api/v1/sessions/{session_id}/activities")
        assert response.status_code == 200
        
        result = response.json()
        assert "activities" in result
        assert len(result["activities"]) == 2
        assert result["total"] == 2

    async def test_get_activity(self, async_client: AsyncClient, sample_session, sample_activity_data):
        """Test getting an activity."""
        # Create activity first
        activity_data = sample_activity_data.copy()
        activity_data["session_id"] = sample_session["id"]
        
        create_response = await async_client.post(
            f"/api/v1/sessions/{sample_session['id']}/activities",
            json=activity_data
        )
        assert create_response.status_code == 201
        created_activity = create_response.json()
        
        # Get the activity
        response = await async_client.get(
            f"/api/v1/activities/{created_activity['id']}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_activity["id"]
        assert data["type"] == activity_data["type"]
        assert data["config"] == activity_data["config"]

    async def test_get_activity_not_found(self, async_client: AsyncClient):
        """Test getting non-existent activity."""
        fake_id = str(uuid4())
        response = await async_client.get(f"/api/v1/activities/{fake_id}")
        assert response.status_code == 404

    async def test_update_activity(self, async_client: AsyncClient, sample_session, sample_activity_data):
        """Test updating an activity."""
        session_id = sample_session["id"]
        
        # Create activity
        create_response = await async_client.post(
            f"/api/v1/sessions/{session_id}/activities/",
            json=sample_activity_data
        )
        activity_id = create_response.json()["id"]
        
        # Update activity
        update_data = {
            "status": "active",
            "config": {
                "question": "Updated question?",
                "options": ["Option A", "Option B"],
                "multiple_choice": True
            }
        }
        
        response = await async_client.put(f"/api/v1/activities/{activity_id}", json=update_data)
        assert response.status_code == 200
        
        updated_activity = response.json()
        assert updated_activity["status"] == "active"
        assert updated_activity["config"]["question"] == "Updated question?"
        assert updated_activity["config"]["multiple_choice"] == True

    async def test_delete_activity(self, async_client: AsyncClient, sample_session, sample_activity_data):
        """Test deleting an activity."""
        session_id = sample_session["id"]
        
        # Create activity
        create_response = await async_client.post(
            f"/api/v1/sessions/{session_id}/activities/",
            json=sample_activity_data
        )
        activity_id = create_response.json()["id"]
        
        # Delete activity
        response = await async_client.delete(f"/api/v1/activities/{activity_id}")
        assert response.status_code == 204
        
        # Verify deletion
        get_response = await async_client.get(f"/api/v1/activities/{activity_id}")
        assert get_response.status_code == 404

    async def test_activity_ordering(self, async_client: AsyncClient, sample_session):
        """Test activities are returned in correct order."""
        session_id = sample_session["id"]
        
        # Create activities with different order indices
        for i in range(3):
            activity_data = {
                "type": "poll",
                "config": {"question": f"Question {i}?"},
                "order_index": 3 - i,  # Reverse order: 3, 2, 1
                "status": "draft"
            }
            await async_client.post(f"/api/v1/sessions/{session_id}/activities", json=activity_data)
        
        response = await async_client.get(f"/api/v1/sessions/{session_id}/activities")
        activities = response.json()["activities"]
        
        # Should be sorted by order_index ascending
        assert activities[0]["order_index"] == 1
        assert activities[1]["order_index"] == 2  
        assert activities[2]["order_index"] == 3

    async def test_activity_status_filtering(self, async_client: AsyncClient, sample_session):
        """Test filtering activities by status."""
        session_id = sample_session["id"]
        
        # Create activities with different statuses
        statuses = ["draft", "active", "completed"]
        for status in statuses:
            activity_data = {
                "type": "poll",
                "config": {"question": f"Question for {status}?"},
                "order_index": 1,
                "status": status
            }
            await async_client.post(f"/api/v1/sessions/{session_id}/activities", json=activity_data)
        
        # Test filtering by active status
        response = await async_client.get(f"/api/v1/sessions/{session_id}/activities?status=active")
        activities = response.json()["activities"]
        
        assert len(activities) == 1
        assert activities[0]["status"] == "active"


class TestActivityService:
    """Test Activity service layer functions."""

    async def test_create_activity_service(self, db_session: AsyncSession):
        """Test ActivityService.create_activity method."""
        # First create a session
        from app.services.session_service import SessionService
        from app.models.schemas import SessionCreate
        
        session_data = SessionCreate(
            title="Test Session",
            description="Test Description",
            max_participants=100
        )
        session = await SessionService.create_session(db_session, session_data)
        
        # Create activity
        activity_data = ActivityCreate(
            type="poll",
            config={"question": "Test question?"},
            order_index=1,
            status=ActivityStatus.DRAFT
        )
        
        activity = await ActivityService.create_activity(
            db=db_session,
            session_id=session.id,
            activity_data=activity_data
        )
        
        assert activity.type == "poll"
        assert activity.config["question"] == "Test question?"
        assert activity.order_index == 1
        assert activity.session_id == session.id

    async def test_get_activity_service(self, db_session: AsyncSession):
        """Test ActivityService.get_activity method."""
        # Create session and activity first
        from app.services.session_service import SessionService
        from app.models.schemas import SessionCreate
        
        session_data = SessionCreate(
            title="Test Session", 
            description="Test Description",
            max_participants=100
        )
        session = await SessionService.create_session(db_session, session_data)
        
        activity_data = ActivityCreate(
            type="word_cloud",
            config={"prompt": "Enter keywords"},
            order_index=1,
            status=ActivityStatus.ACTIVE
        )
        
        created_activity = await ActivityService.create_activity(
            db=db_session,
            session_id=session.id,
            activity_data=activity_data
        )
        
        # Test get_activity
        retrieved_activity = await ActivityService.get_activity(
            db=db_session,
            activity_id=created_activity.id
        )
        
        assert retrieved_activity is not None
        assert retrieved_activity.id == created_activity.id
        assert retrieved_activity.type == "word_cloud"

    async def test_update_activity_service(self, db_session: AsyncSession):
        """Test ActivityService.update_activity method.""" 
        # Create session and activity first
        from app.services.session_service import SessionService
        from app.models.schemas import SessionCreate
        
        session_data = SessionCreate(
            title="Test Session",
            description="Test Description", 
            max_participants=100
        )
        session = await SessionService.create_session(db_session, session_data)
        
        activity_data = ActivityCreate(
            type="qa",
            config={"allow_anonymous": True},
            order_index=1,
            status=ActivityStatus.DRAFT
        )
        
        activity = await ActivityService.create_activity(
            db=db_session,
            session_id=session.id,
            activity_data=activity_data
        )
        
        # Update activity
        update_data = ActivityUpdate(
            status=ActivityStatus.ACTIVE,
            config={"allow_anonymous": False, "moderated": True}
        )
        
        updated_activity = await ActivityService.update_activity(
            db=db_session,
            activity_id=activity.id,
            activity_data=update_data
        )
        
        assert updated_activity.status == ActivityStatus.ACTIVE
        assert updated_activity.config["allow_anonymous"] == False
        assert updated_activity.config["moderated"] == True

    async def test_delete_activity_service(self, db_session: AsyncSession):
        """Test ActivityService.delete_activity method."""
        # Create session and activity first
        from app.services.session_service import SessionService
        from app.models.schemas import SessionCreate
        
        session_data = SessionCreate(
            title="Test Session",
            description="Test Description",
            max_participants=100
        )
        session = await SessionService.create_session(db_session, session_data)
        
        activity_data = ActivityCreate(
            type="planning_poker",
            config={"scale": [1, 2, 3, 5, 8]},
            order_index=1,
            status=ActivityStatus.DRAFT  
        )
        
        activity = await ActivityService.create_activity(
            db=db_session,
            session_id=session.id,
            activity_data=activity_data
        )
        
        # Delete activity
        success = await ActivityService.delete_activity(
            db=db_session,
            activity_id=activity.id
        )
        
        assert success == True
        
        # Verify deletion
        deleted_activity = await ActivityService.get_activity(
            db=db_session,
            activity_id=activity.id
        )
        assert deleted_activity is None
