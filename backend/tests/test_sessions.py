"""
Tests for session API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SessionStatus
from app.models.schemas import SessionCreate
from app.services.session_service import SessionService


class TestSessionAPI:
    """Test session API endpoints."""

    @pytest.mark.asyncio
    async def test_create_session(self, client: TestClient, sample_session_data):
        """Test creating a new session."""
        response = client.post("/api/v1/sessions/", json=sample_session_data)

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == sample_session_data["title"]
        assert data["description"] == sample_session_data["description"]
        assert data["max_participants"] == sample_session_data["max_participants"]
        assert data["status"] == SessionStatus.DRAFT
        assert data["qr_code"] is not None
        assert data["admin_code"] is not None
        assert len(data["qr_code"]) == 8
        assert len(data["admin_code"]) == 6

    @pytest.mark.asyncio
    async def test_create_session_validation(self, client: TestClient):
        """Test session creation validation."""
        # Empty title
        response = client.post("/api/v1/sessions/", json={"title": ""})
        assert response.status_code == 422

        # Invalid max_participants
        response = client.post(
            "/api/v1/sessions/", json={"title": "Test", "max_participants": -1}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_session(
        self, client: TestClient, db_session: AsyncSession, sample_session_create
    ):
        """Test getting a session by ID."""
        # Create session
        session = await SessionService.create_session(db_session, sample_session_create)

        # Get session
        response = client.get(f"/api/v1/sessions/{session.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == session.id
        assert data["title"] == session.title
        assert "activities" in data
        assert "participants" in data

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, client: TestClient):
        """Test getting a non-existent session."""
        response = client.get("/api/v1/sessions/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_sessions(self, client: TestClient, db_session: AsyncSession):
        """Test listing sessions."""
        # Create multiple sessions
        for i in range(3):
            session_create = SessionCreate(
                title=f"Test Session {i}",
                description=f"Description {i}",
                max_participants=50 + i,
            )
            await SessionService.create_session(db_session, session_create)

        # List sessions
        response = client.get("/api/v1/sessions/")

        assert response.status_code == 200
        data = response.json()

        assert len(data["sessions"]) == 3
        assert data["total"] == 3
        assert data["offset"] == 0
        assert data["limit"] == 100

    @pytest.mark.asyncio
    async def test_update_session(
        self, client: TestClient, db_session: AsyncSession, sample_session_create
    ):
        """Test updating a session."""
        # Create session
        session = await SessionService.create_session(db_session, sample_session_create)

        # Update session
        update_data = {"title": "Updated Session", "status": SessionStatus.ACTIVE}
        response = client.put(f"/api/v1/sessions/{session.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == update_data["title"]
        assert data["status"] == SessionStatus.ACTIVE
        assert data["started_at"] is not None

    @pytest.mark.asyncio
    async def test_update_session_not_found(self, client: TestClient):
        """Test updating a non-existent session."""
        response = client.put("/api/v1/sessions/999", json={"title": "Updated"})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_session(
        self, client: TestClient, db_session: AsyncSession, sample_session_create
    ):
        """Test deleting a session."""
        # Create session
        session = await SessionService.create_session(db_session, sample_session_create)

        # Delete session
        response = client.delete(f"/api/v1/sessions/{session.id}")
        assert response.status_code == 204

        # Verify session is deleted
        response = client.get(f"/api/v1/sessions/{session.id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_session_not_found(self, client: TestClient):
        """Test deleting a non-existent session."""
        response = client.delete("/api/v1/sessions/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_session_by_code(
        self, client: TestClient, db_session: AsyncSession, sample_session_create
    ):
        """Test getting a session by QR code."""
        # Create session
        session = await SessionService.create_session(db_session, sample_session_create)

        # Get by QR code
        response = client.get(f"/api/v1/sessions/code/{session.qr_code}?code_type=qr")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == session.id
        assert data["qr_code"] is None  # Should be hidden for participant access

        # Get by admin code
        response = client.get(
            f"/api/v1/sessions/code/{session.admin_code}?code_type=admin"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == session.id
        assert data["qr_code"] == session.qr_code  # Should be visible for admin access

    @pytest.mark.asyncio
    async def test_get_session_by_invalid_code(self, client: TestClient):
        """Test getting a session with invalid code."""
        response = client.get("/api/v1/sessions/code/INVALID")
        assert response.status_code == 404

        # Invalid code type
        response = client.get("/api/v1/sessions/code/INVALID?code_type=invalid")
        assert response.status_code == 400
