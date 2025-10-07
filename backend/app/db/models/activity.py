"""Activity model for the activity framework."""
from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.db.enums import ActivityStatus

if TYPE_CHECKING:
    from .session import Session
    from .user_response import UserResponse


class Activity(Base):
    """Activity model with JSONB configuration storage."""
    __tablename__ = "activities"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(50))
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    order_index: Mapped[int] = mapped_column(Integer)
    status: Mapped[ActivityStatus] = mapped_column(Enum(ActivityStatus), default=ActivityStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="activities")
    user_responses: Mapped[List["UserResponse"]] = relationship("UserResponse", back_populates="activity", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, type={self.type}, status={self.status.value})>"