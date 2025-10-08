"""Pydantic schemas for Activity operations with JSONB support."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.db.enums import ActivityStatus


class ActivityBase(BaseModel):
    """Base schema for Activity."""

    type: str = Field(..., description="Type of the activity")
    config: dict[str, Any] = Field(
        default_factory=dict, description="JSONB configuration data"
    )
    order_index: int = Field(default=0, description="Order index for the activity")

    model_config = ConfigDict(use_enum_values=True)


class ActivityCreate(ActivityBase):
    """Schema for creating a new Activity."""

    status: Optional[ActivityStatus] = Field(
        default=ActivityStatus.DRAFT, description="Status of the activity"
    )


class ActivityUpdate(BaseModel):
    """Schema for updating an Activity."""

    model_config = ConfigDict(use_enum_values=True)

    type: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    order_index: Optional[int] = None
    status: Optional[ActivityStatus] = None


class Activity(ActivityBase):
    """Schema for Activity response."""

    id: UUID
    session_id: int
    status: ActivityStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class ActivityList(BaseModel):
    """Schema for list of activities."""

    activities: list[Activity]
    total: int
