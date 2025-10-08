"""
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.db.enums import ActivityStatus, SessionStatus, ActivityType, ParticipantRole
from app.models.jsonb_schemas.user_response import UserResponse


# Base models
class BaseResponse(BaseModel):
    """Base response model."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


# Session models
class SessionCreate(BaseModel):
    """Session creation request model."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    max_participants: int = Field(default=100, ge=1, le=1000)


class SessionUpdate(BaseModel):
    """Session update request model."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    max_participants: Optional[int] = Field(None, ge=1, le=1000)
    status: Optional[SessionStatus] = None

    model_config = ConfigDict(use_enum_values=True)


class SessionResponse(BaseResponse):
    """Session response model."""

    title: str
    description: Optional[str]
    status: SessionStatus
    qr_code: Optional[str]
    admin_code: Optional[str]
    max_participants: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    participant_count: int = 0
    activity_count: int = 0


class SessionDetail(SessionResponse):
    """Detailed session response with activities and participants."""

    activities: list["ActivityResponse"] = []
    participants: list["ParticipantStatus"] = []


# Activity models
class ActivityCreate(BaseModel):
    """Activity creation request model."""

    model_config = ConfigDict(use_enum_values=True)

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    activity_type: ActivityType
    configuration: dict[str, Any] = Field(default_factory=dict)
    order_index: int = Field(default=0, ge=0)


class ActivityUpdate(BaseModel):
    """Activity update request model."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Optional[dict[str, Any]] = None
    order_index: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ActivityResponse(BaseResponse):
    """Activity response model."""

    session_id: int
    title: str
    description: Optional[str]
    activity_type: ActivityType
    configuration: dict[str, Any]
    is_active: bool
    order_index: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    response_count: int = 0


# Participant models
class ParticipantJoinRequest(BaseModel):
    """Session join request model."""

    nickname: str = Field(..., min_length=1, max_length=50)


class ParticipantJoinResponse(BaseModel):
    """Session join response model."""

    participant_id: str  # UUID as string
    session_state: dict[str, Any]  # Current activity and state info

    class Config:
        from_attributes = True


class ParticipantCreate(BaseModel):
    """Participant creation request model."""

    model_config = ConfigDict(use_enum_values=True)

    display_name: str = Field(..., min_length=1, max_length=100)
    role: ParticipantRole = ParticipantRole.PARTICIPANT


class ParticipantUpdate(BaseModel):
    """Participant update request model."""

    model_config = ConfigDict(use_enum_values=True)

    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[ParticipantRole] = None
    is_active: Optional[bool] = None


class ParticipantResponse(BaseResponse):
    """Participant response model."""

    session_id: int
    display_name: str
    role: ParticipantRole
    is_active: bool


class ParticipantHeartbeatRequest(BaseModel):
    """Participant heartbeat request model."""

    activity_context: Optional[dict[str, Any]] = None


class ParticipantHeartbeatResponse(BaseModel):
    """Participant heartbeat response model."""

    status: str  # "online", "idle", "disconnected"
    activity_context: dict[str, Any]
    updated_at: datetime

    class Config:
        from_attributes = True


class NicknameValidationResponse(BaseModel):
    """Nickname validation response model."""

    available: bool
    suggested_nickname: Optional[str] = None


class ParticipantStatus(BaseModel):
    """Computed participant status model."""

    participant_id: str
    nickname: str
    status: str  # "online", "idle", "disconnected"
    joined_at: datetime
    last_seen: datetime

    class Config:
        from_attributes = True


class ParticipantListResponse(BaseModel):
    """Participant list response model."""

    participants: list[ParticipantStatus]
    total_count: int


# Activity Response models
class ActivityResponseCreate(BaseModel):
    """Activity response creation request model."""

    response_data: dict[str, Any]


class ActivityResponseUpdate(BaseModel):
    """Activity response update request model."""

    response_data: dict[str, Any]


class ActivityResponseResponse(BaseResponse):
    """Activity response response model."""

    activity_id: int
    participant_id: int
    response_data: dict[str, Any]


# List response models
class SessionList(BaseModel):
    """Session list response model."""

    sessions: list[SessionResponse]
    total: int
    offset: int
    limit: int


class ActivityList(BaseModel):
    """Activity list response model."""

    activities: list[ActivityResponse]
    total: int


class ParticipantList(BaseModel):
    """Participant list response model."""

    participants: list[ParticipantStatus]
    total: int


# Status and polling models
class SessionStatusResponse(BaseModel):
    """Session status for real-time polling."""

    session_id: int
    status: SessionStatus
    current_activity_id: Optional[UUID] = None
    participant_count: int
    last_updated: datetime

    model_config = ConfigDict(use_enum_values=True)


class ActivityStatusResponse(BaseModel):
    """Activity status for real-time polling."""

    activity_id: UUID
    status: ActivityStatus
    response_count: int
    last_response_at: Optional[datetime] = None
    last_updated: datetime

    model_config = ConfigDict(use_enum_values=True)


class IncrementalResponseList(BaseModel):
    """Schema for incremental response updates since timestamp."""

    items: list[UserResponse] = []
    since: datetime
    count: int


# Error models
class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str
    error_type: str = "ValidationError"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health check model
class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "0.1.0"


# Framework-Enhanced Models
class ActivityTypeResponse(BaseModel):
    """Activity type information response."""

    id: str = Field(..., description="Unique activity type identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Description of the activity type")
    version: str = Field(..., description="Activity type version")


class ActivityTypesListResponse(BaseModel):
    """List of available activity types response."""

    activity_types: list[ActivityTypeResponse]


class ActivityTypeSchemaResponse(BaseModel):
    """Activity type schema response."""

    activity_type: str = Field(..., description="Activity type identifier")
    schema: dict[str, Any] = Field(
        ..., description="JSON schema for activity configuration"
    )


class FrameworkActivityCreate(BaseModel):
    """Framework-enhanced activity creation request."""

    activity_type: str = Field(..., description="Type of activity to create")
    title: str = Field(..., min_length=1, max_length=500, description="Activity title")
    description: Optional[str] = Field(
        None, description="Optional activity description"
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict, description="Activity-specific configuration"
    )
    activity_metadata: Optional[dict[str, Any]] = Field(
        None, description="Framework metadata"
    )
    order_index: int = Field(
        default=0, ge=0, description="Order index for the activity"
    )


class ActivityTransitionRequest(BaseModel):
    """Activity state transition request."""

    target_state: str = Field(
        ...,
        pattern="^(draft|published|active|expired)$",
        description="Target state to transition to",
    )
    reason: Optional[str] = Field(
        None, max_length=500, description="Optional reason for the transition"
    )
    force: bool = Field(default=False, description="Force transition (skip validation)")


class ActivityValidationRequest(BaseModel):
    """Activity configuration validation request."""

    activity_type: str = Field(..., description="Activity type identifier")
    configuration: dict[str, Any] = Field(..., description="Configuration to validate")


class ActivityValidationResponse(BaseModel):
    """Activity configuration validation response."""

    valid: bool = Field(..., description="Whether the configuration is valid")
    errors: list[str] = Field(
        default_factory=list, description="List of validation errors"
    )
    warnings: list[str] = Field(
        default_factory=list, description="List of validation warnings"
    )


class ActivityResponseSubmissionRequest(BaseModel):
    """Framework activity response submission request."""

    response_data: dict[str, Any] = Field(
        ..., description="Response data from participant"
    )


class ActivityResultsResponse(BaseModel):
    """Activity results response."""

    results: dict[str, Any] = Field(..., description="Calculated activity results")
    last_updated: datetime = Field(..., description="When results were last calculated")


class FrameworkActivityStatusResponse(BaseModel):
    """Enhanced activity status response with framework information."""

    activity_id: UUID = Field(..., description="Activity ID")
    status: ActivityStatus = Field(..., description="Legacy activity status")
    state: str = Field(..., description="Framework activity state")
    response_count: int = Field(..., description="Number of responses")
    expires_at: Optional[datetime] = Field(None, description="When activity expires")
    activity_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Activity metadata"
    )
    valid_transitions: list[str] = Field(
        default_factory=list, description="Valid state transitions"
    )
    results: Optional[dict[str, Any]] = Field(
        None, description="Calculated results if available"
    )
    last_response_at: Optional[datetime] = Field(
        None, description="Last response timestamp"
    )
    last_updated: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(use_enum_values=True)


# Update forward references
SessionDetail.model_rebuild()
ActivityResponse.model_rebuild()
ParticipantStatus.model_rebuild()
IncrementalResponseList.model_rebuild()
