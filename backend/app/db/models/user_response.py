"""User Response model for activity framework."""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from .activity import Activity
    from .participant import Participant
    from .session import Session


class UserResponse(Base):
    """User Response model with JSONB response data storage."""
    __tablename__ = "user_responses"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    activity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("activities.id", ondelete="CASCADE"))
    participant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"))
    response_data: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="user_responses")
    activity: Mapped["Activity"] = relationship("Activity", back_populates="user_responses")
    participant: Mapped["Participant"] = relationship("Participant", back_populates="responses")
    
    def __repr__(self) -> str:
        return f"<UserResponse(id={self.id}, activity_id={self.activity_id}, participant_id={self.participant_id})>"