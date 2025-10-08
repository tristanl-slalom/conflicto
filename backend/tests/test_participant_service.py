"""
Unit tests for ParticipantService.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.services.participant_service import ParticipantService


class TestParticipantStatusComputation:
    """Test participant status computation logic."""

    def test_compute_status_online(self):
        """Test status computation for online participant."""
        service = ParticipantService(None)
        recent_time = datetime.now(timezone.utc) - timedelta(seconds=15)
        status = service._compute_participant_status(recent_time)
        assert status == "online"

    def test_compute_status_idle(self):
        """Test status computation for idle participant."""
        service = ParticipantService(None)
        idle_time = datetime.now(timezone.utc) - timedelta(seconds=60)
        status = service._compute_participant_status(idle_time)
        assert status == "idle"

    def test_compute_status_disconnected(self):
        """Test status computation for disconnected participant."""
        service = ParticipantService(None)
        old_time = datetime.now(timezone.utc) - timedelta(seconds=300)
        status = service._compute_participant_status(old_time)
        assert status == "disconnected"

    def test_compute_status_naive_datetime(self):
        """Test status computation with naive datetime (no timezone)."""
        service = ParticipantService(None)
        naive_time = datetime.now() - timedelta(seconds=15)
        status = service._compute_participant_status(naive_time)
        assert status == "online"


class TestParticipantServiceConstants:
    """Test ParticipantService constants."""

    def test_service_constants(self):
        """Test service threshold constants."""
        service = ParticipantService(None)
        assert service.ONLINE_THRESHOLD == 30
        assert service.IDLE_THRESHOLD == 120

    def test_service_initialization_with_db(self, db_session):
        """Test service initialization with database session."""
        service = ParticipantService(db_session)
        assert service.db == db_session


class TestNicknameValidation:
    """Test nickname validation business logic."""

    async def test_nickname_validation_available_nickname(self, db_session):
        """Test validation of available nickname."""
        service = ParticipantService(db_session)
        result = await service.validate_nickname(1, "newuser")

        # Should be available since no participant exists with this nickname
        assert result.available is True
        assert result.suggested_nickname is None

    async def test_nickname_validation_empty_string(self, db_session):
        """Test validation of empty nickname."""
        service = ParticipantService(db_session)
        result = await service.validate_nickname(1, "")

        # Empty string is treated as available (no validation for emptiness)
        assert result.available is True
        assert result.suggested_nickname is None

    async def test_nickname_validation_unicode_characters(self, db_session):
        """Test validation with Unicode characters."""
        service = ParticipantService(db_session)
        unicode_nickname = "用户名测试"  # Chinese characters
        result = await service.validate_nickname(1, unicode_nickname)

        # Should handle Unicode correctly
        assert result.available is True
        assert result.suggested_nickname is None


class TestIntegrationWithRealDB:
    """Integration tests with real database session."""

    async def test_get_participant_count_empty_session(self, db_session):
        """Test getting participant count for empty session."""
        service = ParticipantService(db_session)
        count = await service.get_participant_count(999)  # Non-existent session
        assert count == 0

    async def test_get_session_participants_empty(self, db_session):
        """Test getting participants for empty session."""
        service = ParticipantService(db_session)
        participants = await service.get_session_participants(999)
        assert participants == []

    async def test_remove_nonexistent_participant(self, db_session):
        """Test removing non-existent participant."""
        service = ParticipantService(db_session)
        result = await service.remove_participant(uuid4())
        assert result is False


class TestServiceMethods:
    """Test that service methods are properly structured."""

    def test_service_methods_have_docstrings(self):
        """Ensure all public methods have docstrings."""
        service = ParticipantService(None)

        public_methods = [
            "join_session",
            "validate_nickname",
            "update_heartbeat",
            "get_session_participants",
            "remove_participant",
            "get_participant_count",
        ]

        for method_name in public_methods:
            method = getattr(service, method_name)
            assert method.__doc__ is not None, f"Method {method_name} missing docstring"
            assert (
                len(method.__doc__.strip()) > 10
            ), f"Method {method_name} has insufficient docstring"
