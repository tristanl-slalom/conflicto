"""Pydantic schemas for Activity models."""
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models import ActivityStatus


class ActivityConfigBase(BaseModel):
    """Base schema for Activity configuration."""
    version: str = Field(default="1.0", description="Configuration schema version")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Activity-specific settings")
    display: Dict[str, str] = Field(default_factory=dict, description="Display configuration")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Activity constraints")


class NewActivityBase(BaseModel):
    """Base schema for New Activity."""
    type: str = Field(..., description="Activity type identifier")
    config: Dict[str, Any] = Field(default_factory=dict, description="Activity configuration in JSON format")
    order_index: int = Field(..., description="Order of activity in session")


class NewActivityCreate(NewActivityBase):
    """Schema for creating a New Activity."""
    pass


class NewActivityUpdate(BaseModel):
    """Schema for updating a New Activity."""
    type: str | None = None
    config: Dict[str, Any] | None = None
    order_index: int | None = None
    status: ActivityStatus | None = None


class NewActivity(NewActivityBase):
    """Schema for New Activity with all fields."""
    id: UUID
    session_id: int
    status: ActivityStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewActivityList(BaseModel):
    """Schema for paginated New Activity list."""
    activities: List[NewActivity]
    total_count: int