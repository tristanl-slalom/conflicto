"""
Tests for Activity API routes and services.
"""
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ActivityStatus
from app.models.jsonb_schemas.activity import ActivityCreate, ActivityUpdate
from app.services.activity_service import ActivityService


class TestActivityAPI:
    """Test Activity API endpoints."""
    
    @pytest.fixture
    async def sample_session(self, db_session: AsyncSession, client: TestClient):
        """Create a sample session for testing."""
        session_data = {
            "title": "Test Session for Activities",
            "description": "A session for testing activities",
            "max_participants": 50
        }
        response = client.post("/api/v1/sessions/", json=session_data)
        assert response.status_code == 201
        return response.json()

    @pytest.fixture
    async def sample_activity_data(self):
        """Sample activity data for testing."""
        return {
            "type": "poll", 
            "config": {
                "question": "What's your favorite color?",
                "options": ["Red", "Blue", "Green", "Yellow"],
                "multiple_choice": False
            },
            "order_index": 1,
            "status": "draft"
        }

    async def test_create_activity(self, client: TestClient, sample_session, sample_activity_data):
        """Test creating a new activity."""
        session_id = sample_session["id"]
        
        response = client.post(
            f"/api/v1/sessions/{session_id}/activities",
            json=sample_activity_data
        )
        
        assert response.status_code == 201
        activity = response.json()
        assert activity["type"] == "poll"
        assert activity["config"]["question"] == "What's your favorite color?"
        assert activity["order_index"] == 1
        assert activity["status"] == "draft"
        assert "id" in activity
        assert activity["session_id"] == session_id

    async def test_create_activity_invalid_session(self, client: TestClient, sample_activity_data):
        """Test creating activity for non-existent session."""
        response = client.post(
            "/api/v1/sessions/99999/activities", 
            json=sample_activity_data
        )
        assert response.status_code == 400

    async def test_get_session_activities(self, client: TestClient, sample_session):
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
        
        client.post(f"/api/v1/sessions/{session_id}/activities", json=activity1_data)
        client.post(f"/api/v1/sessions/{session_id}/activities", json=activity2_data)
        
        response = client.get(f"/api/v1/sessions/{session_id}/activities")
        assert response.status_code == 200
        
        result = response.json()
        assert "activities" in result
        assert len(result["activities"]) == 2
        assert result["total"] == 2

    async def test_get_activity_by_id(self, client: TestClient, sample_session, sample_activity_data):
        """Test getting a specific activity by ID."""
        session_id = sample_session["id"]
        
        # Create activity
        create_response = client.post(
            f"/api/v1/sessions/{session_id}/activities",
            json=sample_activity_data
        )
        activity_id = create_response.json()["id"]
        
        # Get activity
        response = client.get(f"/api/v1/activities/{activity_id}")
        assert response.status_code == 200
        
        activity = response.json()
        assert activity["id"] == activity_id
        assert activity["type"] == "poll"

    async def test_get_activity_not_found(self, client: TestClient):
        """Test getting non-existent activity."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/activities/{fake_id}")
        assert response.status_code == 404

    async def test_update_activity(self, client: TestClient, sample_session, sample_activity_data):
        """Test updating an activity."""
        session_id = sample_session["id"]
        
        # Create activity
        create_response = client.post(
            f"/api/v1/sessions/{session_id}/activities",
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
        
        response = client.put(f"/api/v1/activities/{activity_id}", json=update_data)
        assert response.status_code == 200
        
        updated_activity = response.json()
        assert updated_activity["status"] == "active"
        assert updated_activity["config"]["question"] == "Updated question?"
        assert updated_activity["config"]["multiple_choice"] == True

    async def test_delete_activity(self, client: TestClient, sample_session, sample_activity_data):
        """Test deleting an activity."""
        session_id = sample_session["id"]
        
        # Create activity
        create_response = client.post(
            f"/api/v1/sessions/{session_id}/activities",
            json=sample_activity_data
        )
        activity_id = create_response.json()["id"]
        
        # Delete activity
        response = client.delete(f"/api/v1/activities/{activity_id}")
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/api/v1/activities/{activity_id}")
        assert get_response.status_code == 404

    async def test_activity_ordering(self, client: TestClient, sample_session):
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
            client.post(f"/api/v1/sessions/{session_id}/activities", json=activity_data)
        
        response = client.get(f"/api/v1/sessions/{session_id}/activities")
        activities = response.json()["activities"]
        
        # Should be sorted by order_index ascending
        assert activities[0]["order_index"] == 1
        assert activities[1]["order_index"] == 2  
        assert activities[2]["order_index"] == 3

    async def test_activity_status_filtering(self, client: TestClient, sample_session):
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
            client.post(f"/api/v1/sessions/{session_id}/activities", json=activity_data)
        
        # Test filtering by active status
        response = client.get(f"/api/v1/sessions/{session_id}/activities?status=active")
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
            status="draft"
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
            status="active"
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
            status="draft"
        )
        
        activity = await ActivityService.create_activity(
            db=db_session,
            session_id=session.id,
            activity_data=activity_data
        )
        
        # Update activity
        update_data = ActivityUpdate(
            status="active",
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
            status="draft"  
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
