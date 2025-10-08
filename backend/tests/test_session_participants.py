"""
Simplified tests for session management functionality.
"""
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SessionStatus
from app.models.schemas import SessionCreate
from app.services.session_service import SessionService


class TestSessionAPI:
    """Test session API endpoints."""
    
    async def test_create_session(self, client: TestClient):
        """Test creating a session via API."""
        session_data = {
            "title": "Test Session",
            "description": "A test session",
            "max_participants": 50
        }
        
        response = client.post("/api/v1/sessions/", json=session_data)
        assert response.status_code == 201
        
        session = response.json()
        assert session["title"] == "Test Session"
        assert session["description"] == "A test session"
        assert session["max_participants"] == 50
        assert session["status"] == "draft"
        assert session["qr_code"] is not None
        assert session["admin_code"] is not None

    async def test_get_session(self, client: TestClient):
        """Test getting a session by ID."""
        # Create session first
        session_data = {
            "title": "Get Test Session",
            "description": "Testing get functionality",
            "max_participants": 25
        }
        create_response = client.post("/api/v1/sessions/", json=session_data)
        session_id = create_response.json()["id"]
        
        # Get the session
        response = client.get(f"/api/v1/sessions/{session_id}")
        assert response.status_code == 200
        
        session = response.json()
        assert session["title"] == "Get Test Session"
        assert session["id"] == session_id

    async def test_update_session(self, client: TestClient):
        """Test updating a session."""
        # Create session first
        session_data = {
            "title": "Original Title",
            "description": "Original description",
            "max_participants": 30
        }
        create_response = client.post("/api/v1/sessions/", json=session_data)
        session_id = create_response.json()["id"]
        
        # Update the session
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        response = client.put(f"/api/v1/sessions/{session_id}", json=update_data)
        assert response.status_code == 200
        
        session = response.json()
        assert session["title"] == "Updated Title"
        assert session["description"] == "Updated description"

    async def test_list_sessions(self, client: TestClient):
        """Test listing sessions."""
        # Create a few sessions
        for i in range(3):
            session_data = {
                "title": f"List Test Session {i+1}",
                "description": f"Test session {i+1}",
                "max_participants": 40
            }
            client.post("/api/v1/sessions/", json=session_data)
        
        # List sessions
        response = client.get("/api/v1/sessions/")
        assert response.status_code == 200
        
        session_list = response.json()
        assert len(session_list["sessions"]) >= 3
        assert "total" in session_list


class TestSessionService:
    """Test session service layer."""

    async def test_create_session_service(self, db_session: AsyncSession):
        """Test creating a session via service layer."""
        session_data = SessionCreate(
            title="Service Test Session",
            description="Testing service layer",
            max_participants=60
        )
        
        session = await SessionService.create_session(db_session, session_data)
        
        assert session.title == "Service Test Session"
        assert session.description == "Testing service layer"
        assert session.max_participants == 60
        assert session.status == SessionStatus.DRAFT
        assert session.qr_code is not None
        assert session.admin_code is not None

    async def test_get_session_service(self, db_session: AsyncSession):
        """Test getting a session via service layer."""
        # Create session first
        session_data = SessionCreate(
            title="Get Service Test",
            description="Testing get via service",
            max_participants=70
        )
        created_session = await SessionService.create_session(db_session, session_data)
        
        # Get the session
        retrieved_session = await SessionService.get_session(db_session, created_session.id)
        
        assert retrieved_session is not None
        assert retrieved_session.title == "Get Service Test"
        assert retrieved_session.id == created_session.id

    async def test_get_session_by_code_service(self, db_session: AsyncSession):
        """Test getting a session by code via service layer."""
        # Create session first
        session_data = SessionCreate(
            title="Code Test Session",
            description="Testing get by code",
            max_participants=80
        )
        created_session = await SessionService.create_session(db_session, session_data)
        
        # Get by QR code
        session_by_qr = await SessionService.get_session_by_code(
            db_session, created_session.qr_code, "qr"
        )
        assert session_by_qr is not None
        assert session_by_qr.id == created_session.id
        
        # Get by admin code
        session_by_admin = await SessionService.get_session_by_code(
            db_session, created_session.admin_code, "admin"
        )
        assert session_by_admin is not None
        assert session_by_admin.id == created_session.id

    async def test_session_stats_service(self, db_session: AsyncSession):
        """Test getting session statistics."""
        # Create session
        session_data = SessionCreate(
            title="Stats Test Session",
            description="Testing statistics",
            max_participants=90
        )
        session = await SessionService.create_session(db_session, session_data)
        
        # Get stats
        stats = await SessionService.get_session_stats(db_session, session.id)
        
        assert "participant_count" in stats
        assert "activity_count" in stats
        assert stats["participant_count"] == 0
        assert stats["activity_count"] == 0
        assert stats["status"] == SessionStatus.DRAFT