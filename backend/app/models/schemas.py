"""
Pydantic models for request/response validation.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.db.models import ActivityType, ParticipantRole, SessionStatus


# Base models
class BaseResponse(BaseModel):
    """Base response model."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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
    participants: list["ParticipantResponse"] = []


# Activity models
class ActivityCreate(BaseModel):
    """Activity creation request model."""

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
class ParticipantCreate(BaseModel):
    """Participant creation request model."""

    display_name: str = Field(..., min_length=1, max_length=100)
    role: ParticipantRole = ParticipantRole.PARTICIPANT


class ParticipantUpdate(BaseModel):
    """Participant update request model."""

    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[ParticipantRole] = None
    is_active: Optional[bool] = None


class ParticipantResponse(BaseResponse):
    """Participant response model."""

    session_id: int
    display_name: str
    role: ParticipantRole
    is_active: bool
    joined_at: datetime
    last_seen_at: datetime


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

    participants: list[ParticipantResponse]
    total: int


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


# Update forward references
SessionDetail.model_rebuild()
ActivityResponse.model_rebuild()
ParticipantResponse.model_rebuild()
