"""Pydantic schemas for User Response models."""
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field


class UserResponseBase(BaseModel):
    """Base schema for User Response."""

    response_data: Dict[str, Any] = Field(
        ..., description="Activity-specific response data in JSON format"
    )


class UserResponseCreate(UserResponseBase):
    """Schema for creating a User Response."""

    pass


class UserResponseUpdate(UserResponseBase):
    """Schema for updating a User Response."""

    pass


class UserResponse(UserResponseBase):
    """Schema for User Response with all fields."""

    id: UUID
    session_id: int
    activity_id: UUID
    participant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponseSummary(BaseModel):
    """Schema for User Response summary statistics."""

    total_responses: int
    unique_participants: int
    last_updated: datetime | None


class UserResponseList(BaseModel):
    """Schema for paginated User Response list with summary."""

    responses: List[UserResponse]
    summary: UserResponseSummary
