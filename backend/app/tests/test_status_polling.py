"""Tests for status polling endpoints."""
from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Activity,
    ActivityStatus,
    Participant,
    Session,
    SessionStatus,
    UserResponse,
)
from app.main import app


@pytest.mark.asyncio
async def test_session_status_polling(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Test session status polling endpoint."""
    # Create test session
    session = Session(
        title="Test Session",
        status=SessionStatus.ACTIVE,
        qr_code="test_qr",
        admin_code="test_admin",
        max_participants=50,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create test participant
    participant = Participant(
        session_id=session.id, display_name="Test Participant", role="participant"
    )
    db_session.add(participant)

    # Create test activity
    activity = Activity(
        session_id=session.id,
        type="poll",
        config={"question": "Test question?"},
        order_index=0,
        status=ActivityStatus.ACTIVE,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)

    # Test session status endpoint
    response = await async_client.get(f"/sessions/{session.id}/status")
    assert response.status_code == 200

    data = response.json()
    assert data["session_id"] == session.id
    assert data["status"] == SessionStatus.ACTIVE
    assert data["current_activity_id"] == str(activity.id)
    assert data["participant_count"] == 1
    assert "last_updated" in data


@pytest.mark.asyncio
async def test_activity_status_polling(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Test activity status polling endpoint."""
    # Create test session
    session = Session(
        title="Test Session",
        status=SessionStatus.ACTIVE,
        qr_code="test_qr",
        admin_code="test_admin",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create test activity
    activity = Activity(
        session_id=session.id,
        type="poll",
        config={"question": "Test question?"},
        order_index=0,
        status=ActivityStatus.ACTIVE,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)

    # Create test participant and responses
    participant = Participant(
        session_id=session.id, display_name="Test Participant", role="participant"
    )
    db_session.add(participant)
    await db_session.commit()
    await db_session.refresh(participant)

    response1 = UserResponse(
        session_id=session.id,
        activity_id=activity.id,
        participant_id=participant.id,
        response_data={"answer": "Yes"},
    )
    db_session.add(response1)
    await db_session.commit()

    # Test activity status endpoint
    response = await async_client.get(
        f"/api/v1/sessions/{session.id}/activities/{activity.id}/status"
    )
    assert response.status_code == 200

    data = response.json()
    assert data["activity_id"] == str(activity.id)
    assert data["status"] == ActivityStatus.ACTIVE
    assert data["response_count"] == 1
    assert "last_response_at" in data
    assert "last_updated" in data


@pytest.mark.asyncio
async def test_incremental_response_updates(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Test incremental response updates endpoint."""
    # Create test session
    session = Session(
        title="Test Session",
        status=SessionStatus.ACTIVE,
        qr_code="test_qr",
        admin_code="test_admin",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create test activity
    activity = Activity(
        session_id=session.id,
        type="poll",
        config={"question": "Test question?"},
        order_index=0,
        status=ActivityStatus.ACTIVE,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)

    # Create test participant
    participant = Participant(
        session_id=session.id, display_name="Test Participant", role="participant"
    )
    db_session.add(participant)
    await db_session.commit()
    await db_session.refresh(participant)

    # Record timestamp before creating responses
    since_timestamp = datetime.utcnow()

    # Create responses after timestamp
    response1 = UserResponse(
        session_id=session.id,
        activity_id=activity.id,
        participant_id=participant.id,
        response_data={"answer": "Yes"},
    )
    db_session.add(response1)
    await db_session.commit()

    # Test incremental updates endpoint
    timestamp_str = since_timestamp.isoformat() + "Z"
    response = await async_client.get(
        f"/api/v1/sessions/{session.id}/activities/{activity.id}/responses/since/{timestamp_str}"
    )
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["response_data"] == {"answer": "Yes"}
    assert "since" in data


@pytest.mark.asyncio
async def test_session_not_found(async_client: AsyncClient):
    """Test session status with non-existent session."""
    response = await async_client.get("/sessions/999999/status")
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_activity_not_found(async_client: AsyncClient, db_session: AsyncSession):
    """Test activity status with non-existent activity."""
    # Create test session
    session = Session(
        title="Test Session",
        status=SessionStatus.ACTIVE,
        qr_code="test_qr",
        admin_code="test_admin",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    fake_activity_id = uuid4()
    response = await async_client.get(
        f"/api/v1/sessions/{session.id}/activities/{fake_activity_id}/status"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_timestamp_format(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Test incremental updates with invalid timestamp format."""
    # Create test session and activity
    session = Session(
        title="Test Session",
        status=SessionStatus.ACTIVE,
        qr_code="test_qr",
        admin_code="test_admin",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    activity = Activity(
        session_id=session.id,
        type="poll",
        config={"question": "Test question?"},
        order_index=0,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)

    # Test with invalid timestamp
    response = await async_client.get(
        f"/api/v1/sessions/{session.id}/activities/{activity.id}/responses/since/invalid-timestamp"
    )
    assert response.status_code == 400
    assert "Invalid timestamp format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_polling_performance(async_client: AsyncClient, db_session: AsyncSession):
    """Test polling endpoints performance with multiple requests."""
    # Create test session
    session = Session(
        title="Test Session",
        status=SessionStatus.ACTIVE,
        qr_code="test_qr",
        admin_code="test_admin",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create multiple participants
    participants = []
    for i in range(10):
        participant = Participant(
            session_id=session.id, display_name=f"Participant {i}", role="participant"
        )
        db_session.add(participant)
        participants.append(participant)

    await db_session.commit()

    # Test multiple rapid polling requests
    import time

    start_time = time.time()

    for _ in range(10):
        response = await async_client.get(f"/sessions/{session.id}/status")
        assert response.status_code == 200

    end_time = time.time()
    avg_response_time = (end_time - start_time) / 10

    # Should complete within 200ms on average
    assert (
        avg_response_time < 0.2
    ), f"Average response time {avg_response_time}s exceeds 200ms"
