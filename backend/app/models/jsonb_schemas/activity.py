"""Pydantic schemas for Activity operations with JSONB support."""
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.db.models import ActivityStatus


class ActivityBase(BaseModel):
    """Base schema for Activity."""
    type: str = Field(..., description="Type of the activity")
    config: Dict[str, Any] = Field(default_factory=dict, description="JSONB configuration data")
    order_index: int = Field(default=0, description="Order index for the activity")


class ActivityCreate(ActivityBase):
    """Schema for creating a new Activity."""
    status: Optional[ActivityStatus] = Field(default=ActivityStatus.DRAFT, description="Status of the activity")


class ActivityUpdate(BaseModel):
    """Schema for updating an Activity."""
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    order_index: Optional[int] = None
    status: Optional[ActivityStatus] = None


class Activity(ActivityBase):
    """Schema for Activity response."""
    id: UUID
    session_id: int
    status: ActivityStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityList(BaseModel):
    """Schema for list of activities."""
    activities: List[Activity]
    total: int
