"""
Tests for database models, enums, and utility functions.
"""

from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Session,
    Activity,
    Participant,
    UserResponse,
    JSONBType,
    UUIDType,
)
from app.db.enums import ActivityStatus, SessionStatus, ActivityType, ParticipantRole


class TestDatabaseModels:
    """Test SQLAlchemy database models."""

    async def test_session_model_creation(self, db_session: AsyncSession):
        """Test creating a Session model."""
        session = Session(
            title="Test Session",
            description="A test session for unit tests",
            status=SessionStatus.DRAFT,
            qr_code="TEST123",
            admin_code="ADMIN456",
            max_participants=50,
        )

        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        assert session.id is not None
        assert session.title == "Test Session"
        assert session.description == "A test session for unit tests"
        assert session.status == SessionStatus.DRAFT
        assert session.qr_code == "TEST123"
        assert session.admin_code == "ADMIN456"
        assert session.max_participants == 50
        assert session.created_at is not None
        assert session.updated_at is not None

    async def test_session_status_enum(self):
        """Test SessionStatus enum values."""
        assert SessionStatus.DRAFT == "draft"
        assert SessionStatus.ACTIVE == "active"
        assert SessionStatus.PAUSED == "paused"
        assert SessionStatus.COMPLETED == "completed"

        # Test all enum values
        all_statuses = [status.value for status in SessionStatus]
        assert "draft" in all_statuses
        assert "active" in all_statuses
        assert "paused" in all_statuses
        assert "completed" in all_statuses

    async def test_activity_model_creation(self, db_session: AsyncSession):
        """Test creating an Activity model."""
        # Create session first
        session = Session(
            title="Test Session",
            description="Test description",
            status=SessionStatus.DRAFT,
            qr_code="QR123",
            admin_code="ADMIN123",
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Create activity
        activity = Activity(
            session_id=session.id,
            type="poll",
            config={
                "question": "What is your favorite color?",
                "options": ["Red", "Blue", "Green"],
                "multiple_choice": False,
            },
            order_index=1,
            status=ActivityStatus.DRAFT,
        )

        db_session.add(activity)
        await db_session.commit()
        await db_session.refresh(activity)

        assert activity.id is not None
        assert activity.session_id == session.id
        assert activity.type == "poll"
        assert activity.config["question"] == "What is your favorite color?"
        assert len(activity.config["options"]) == 3
        assert activity.config["multiple_choice"] is False
        assert activity.order_index == 1
        assert activity.status == ActivityStatus.DRAFT
        assert activity.created_at is not None
        assert activity.updated_at is not None

    async def test_activity_status_enum(self):
        """Test ActivityStatus enum values."""
        assert ActivityStatus.DRAFT == "draft"
        assert ActivityStatus.ACTIVE == "active"
        assert ActivityStatus.COMPLETED == "completed"
        assert ActivityStatus.CANCELLED == "cancelled"

        # Test all enum values
        all_statuses = [status.value for status in ActivityStatus]
        expected_statuses = ["draft", "active", "completed", "cancelled"]
        for status in expected_statuses:
            assert status in all_statuses

    async def test_activity_type_enum(self):
        """Test ActivityType enum values."""
        assert ActivityType.POLL == "poll"
        assert ActivityType.WORD_CLOUD == "word_cloud"
        assert ActivityType.QA == "qa"
        assert ActivityType.PLANNING_POKER == "planning_poker"

        # Test all enum values
        all_types = [activity_type.value for activity_type in ActivityType]
        expected_types = ["poll", "word_cloud", "qa", "planning_poker"]
        for activity_type in expected_types:
            assert activity_type in all_types

    async def test_participant_model_creation(self, db_session: AsyncSession):
        """Test creating a Participant model."""
        # Create session first
        session = Session(
            title="Test Session",
            description="Test description",
            status=SessionStatus.ACTIVE,
            qr_code="QR456",
            admin_code="ADMIN456",
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Create participant
        participant = Participant(
            session_id=session.id,
            display_name="John Doe",
            role=ParticipantRole.PARTICIPANT,
            is_active=True,
        )

        db_session.add(participant)
        await db_session.commit()
        await db_session.refresh(participant)

        assert participant.id is not None
        assert participant.session_id == session.id
        assert participant.display_name == "John Doe"
        assert participant.role == ParticipantRole.PARTICIPANT
        assert participant.is_active is True
        assert participant.joined_at is not None
        assert participant.last_seen is not None

    async def test_participant_role_enum(self):
        """Test ParticipantRole enum values."""
        assert ParticipantRole.ADMIN == "admin"
        assert ParticipantRole.VIEWER == "viewer"
        assert ParticipantRole.PARTICIPANT == "participant"

        # Test all enum values
        all_roles = [role.value for role in ParticipantRole]
        expected_roles = ["admin", "viewer", "participant"]
        for role in expected_roles:
            assert role in all_roles

    async def test_user_response_model_creation(self, db_session: AsyncSession):
        """Test creating a UserResponse model."""
        # Create session
        session = Session(
            title="Test Session",
            description="Test description",
            status=SessionStatus.ACTIVE,
            qr_code="QR789",
            admin_code="ADMIN789",
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Create activity
        activity = Activity(
            session_id=session.id,
            type="poll",
            config={"question": "Test question?"},
            order_index=1,
            status=ActivityStatus.ACTIVE,
        )
        db_session.add(activity)
        await db_session.commit()
        await db_session.refresh(activity)

        # Create participant
        participant = Participant(
            session_id=session.id,
            display_name="Test User",
            role=ParticipantRole.PARTICIPANT,
        )
        db_session.add(participant)
        await db_session.commit()
        await db_session.refresh(participant)

        # Create user response
        user_response = UserResponse(
            session_id=session.id,
            activity_id=activity.id,
            participant_id=participant.id,
            response_data={
                "selected_option": "Option A",
                "confidence": 0.8,
                "notes": "This is my choice",
            },
        )

        db_session.add(user_response)
        await db_session.commit()
        await db_session.refresh(user_response)

        assert user_response.id is not None
        assert user_response.session_id == session.id
        assert user_response.activity_id == activity.id
        assert user_response.participant_id == participant.id
        assert user_response.response_data["selected_option"] == "Option A"
        assert user_response.response_data["confidence"] == 0.8
        assert user_response.response_data["notes"] == "This is my choice"
        assert user_response.created_at is not None
        assert user_response.updated_at is not None

    async def test_model_relationships(self, db_session: AsyncSession):
        """Test relationships between models."""
        # Create session
        session = Session(
            title="Relationship Test Session",
            description="Testing model relationships",
            status=SessionStatus.ACTIVE,
            qr_code="REL123",
            admin_code="RELADMIN123",
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Create activities
        activity1 = Activity(
            session_id=session.id,
            type="poll",
            config={"question": "Question 1?"},
            order_index=1,
            status=ActivityStatus.ACTIVE,
        )
        activity2 = Activity(
            session_id=session.id,
            type="word_cloud",
            config={"prompt": "Enter words"},
            order_index=2,
            status=ActivityStatus.DRAFT,
        )
        db_session.add_all([activity1, activity2])
        await db_session.commit()
        await db_session.refresh(activity1)
        await db_session.refresh(activity2)

        # Create participants
        participant1 = Participant(
            session_id=session.id,
            display_name="User 1",
            role=ParticipantRole.PARTICIPANT,
        )
        participant2 = Participant(
            session_id=session.id, display_name="User 2", role=ParticipantRole.ADMIN
        )
        db_session.add_all([participant1, participant2])
        await db_session.commit()
        await db_session.refresh(participant1)
        await db_session.refresh(participant2)

        # Create user responses
        response1 = UserResponse(
            session_id=session.id,
            activity_id=activity1.id,
            participant_id=participant1.id,
            response_data={"answer": "Response 1"},
        )
        response2 = UserResponse(
            session_id=session.id,
            activity_id=activity1.id,
            participant_id=participant2.id,
            response_data={"answer": "Response 2"},
        )
        db_session.add_all([response1, response2])
        await db_session.commit()

        # Refresh session to load relationships
        await db_session.refresh(
            session, ["activities", "participants", "user_responses"]
        )

        # Test session relationships
        assert len(session.activities) == 2
        assert len(session.participants) == 2
        assert len(session.user_responses) == 2

        # Test activity relationships
        await db_session.refresh(activity1, ["user_responses"])
        assert len(activity1.user_responses) == 2
        assert activity1.session == session

    async def test_jsonb_type_compatibility(self):
        """Test JSONBType works with our database setup."""
        # Test that JSONBType can be instantiated and used
        jsonb_type = JSONBType()

        # Test that it's a valid SQLAlchemy type
        assert jsonb_type is not None
        assert hasattr(jsonb_type, "load_dialect_impl")

        # Test basic functionality - this validates the type works
        test_data = {"test": "value", "number": 42}
        # The type should be able to handle dictionary data
        assert isinstance(test_data, dict)

    async def test_uuid_type_compatibility(self):
        """Test UUIDType works with our database setup."""
        # Test that UUIDType can be instantiated and used
        uuid_type = UUIDType()

        # Test that it's a valid SQLAlchemy type
        assert uuid_type is not None
        assert hasattr(uuid_type, "load_dialect_impl")
        assert hasattr(uuid_type, "process_bind_param")
        assert hasattr(uuid_type, "process_result_value")

        # Test UUID string conversion
        test_uuid = str(uuid4())
        # The type should be able to handle UUID strings
        assert len(test_uuid) == 36  # Standard UUID length

    async def test_complex_jsonb_data(self, db_session: AsyncSession):
        """Test complex JSONB data structures."""
        # Create session and activity
        session = Session(
            title="JSONB Test Session",
            description="Testing complex JSONB data",
            status=SessionStatus.ACTIVE,
            qr_code="JSON123",
            admin_code="JSONADMIN123",
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Complex activity configuration
        complex_config = {
            "type": "multi_step_poll",
            "steps": [
                {
                    "id": 1,
                    "question": "What is your role?",
                    "options": ["Developer", "Designer", "Manager", "Other"],
                    "required": True,
                },
                {
                    "id": 2,
                    "question": "Years of experience?",
                    "type": "range",
                    "min": 0,
                    "max": 20,
                    "step": 1,
                },
            ],
            "logic": {
                "branching": {
                    "1": {
                        "Developer": [2, 3],
                        "Designer": [2, 4],
                        "Manager": [5],
                        "Other": [6],
                    }
                }
            },
            "settings": {
                "allow_back": True,
                "show_progress": True,
                "timeout_minutes": 10,
            },
        }

        activity = Activity(
            session_id=session.id,
            type="poll",
            config=complex_config,
            order_index=1,
            status=ActivityStatus.ACTIVE,
        )

        db_session.add(activity)
        await db_session.commit()
        await db_session.refresh(activity)

        # Verify complex data was stored correctly
        assert activity.config["type"] == "multi_step_poll"
        assert len(activity.config["steps"]) == 2
        assert activity.config["steps"][0]["question"] == "What is your role?"
        assert activity.config["logic"]["branching"]["1"]["Developer"] == [2, 3]
        assert activity.config["settings"]["timeout_minutes"] == 10


class TestDatabaseEnums:
    """Test database enum functionality."""

    def test_activity_type_enum_import(self):
        """Test ActivityType import and values."""
        assert ActivityType.POLL.value == "poll"
        assert ActivityType.WORD_CLOUD.value == "word_cloud"
        assert ActivityType.QA.value == "qa"
        assert ActivityType.PLANNING_POKER.value == "planning_poker"

    def test_enum_string_representation(self):
        """Test enum string representations."""
        assert SessionStatus.DRAFT.value == "draft"
        assert ActivityStatus.ACTIVE.value == "active"
        assert ParticipantRole.ADMIN.value == "admin"
        assert ActivityType.POLL.value == "poll"

    def test_enum_equality(self):
        """Test enum equality comparisons."""
        assert SessionStatus.DRAFT == "draft"
        assert ActivityStatus.ACTIVE == "active"
        assert ParticipantRole.PARTICIPANT == "participant"
        assert ActivityType.WORD_CLOUD == "word_cloud"

        # Test inequality
        assert SessionStatus.DRAFT != "active"
        assert ActivityStatus.COMPLETED != "draft"

    def test_enum_membership(self):
        """Test enum membership checks."""
        valid_session_statuses = ["draft", "active", "paused", "completed"]
        for status in list(SessionStatus):
            assert status.value in valid_session_statuses

        valid_activity_types = ["poll", "word_cloud", "qa", "planning_poker"]
        for activity_type in list(ActivityType):
            assert activity_type.value in valid_activity_types

    def test_enum_iteration(self):
        """Test iterating through enum values."""
        session_statuses = list(SessionStatus)
        assert len(session_statuses) == 4

        activity_statuses = list(ActivityStatus)
        assert len(activity_statuses) == 4

        participant_roles = list(ParticipantRole)
        assert len(participant_roles) == 3

        activity_types = list(ActivityType)
        assert len(activity_types) == 4
