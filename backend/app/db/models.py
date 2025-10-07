"""
SQLAlchemy models for the Caja application.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class SessionStatus(str, Enum):
    """Session status enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"


class ActivityType(str, Enum):
    """Activity type enumeration."""

    POLL = "poll"
    WORD_CLOUD = "word_cloud"
    QA = "qa"
    PLANNING_POKER = "planning_poker"


class ParticipantRole(str, Enum):
    """Participant role enumeration."""

    ADMIN = "admin"
    VIEWER = "viewer"
    PARTICIPANT = "participant"


class Session(Base):
    """Session model representing a live event session."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default=SessionStatus.DRAFT, nullable=False)
    qr_code = Column(String(255), unique=True, index=True)
    admin_code = Column(String(255), unique=True, index=True)
    max_participants = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    activities = relationship(
        "Activity", back_populates="session", cascade="all, delete-orphan"
    )
    participants = relationship(
        "Participant", back_populates="session", cascade="all, delete-orphan"
    )
    new_activities = relationship(
        "NewActivity", back_populates="session", cascade="all, delete-orphan"
    )
    user_responses = relationship(
        "UserResponse", back_populates="session", cascade="all, delete-orphan"
    )


class Activity(Base):
    """Activity model representing activities within a session."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    activity_type = Column(String(50), nullable=False)
    configuration = Column(JSON, default=dict)  # Store activity-specific config
    is_active = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    session = relationship("Session", back_populates="activities")
    responses = relationship(
        "ActivityResponse", back_populates="activity", cascade="all, delete-orphan"
    )


class Participant(Base):
    """Participant model representing users in a session."""

    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    display_name = Column(String(100), nullable=False)
    role = Column(String(20), default=ParticipantRole.PARTICIPANT, nullable=False)
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="participants")
    responses = relationship(
        "ActivityResponse", back_populates="participant", cascade="all, delete-orphan"
    )
    user_responses = relationship(
        "UserResponse", back_populates="participant", cascade="all, delete-orphan"
    )


class ActivityResponse(Base):
    """Activity response model for storing participant responses."""

    __tablename__ = "activity_responses"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    response_data = Column(JSON, nullable=False)  # Store response content
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    activity = relationship("Activity", back_populates="responses")
    participant = relationship("Participant", back_populates="responses")


class ActivityStatus(str, Enum):
    """Activity status enumeration for new activity framework."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class NewActivity(Base):
    """New Activity model with JSONB configuration storage."""
    __tablename__ = "new_activities"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(50))
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    order_index: Mapped[int] = mapped_column(Integer)
    status: Mapped[ActivityStatus] = mapped_column(String(20), default=ActivityStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="new_activities")
    user_responses = relationship("UserResponse", back_populates="new_activity", cascade="all, delete-orphan")


class UserResponse(Base):
    """User Response model with JSONB response data storage."""
    __tablename__ = "user_responses"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    activity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("new_activities.id", ondelete="CASCADE"))
    participant_id: Mapped[int] = mapped_column(Integer, ForeignKey("participants.id", ondelete="CASCADE"))
    response_data: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="user_responses")
    new_activity = relationship("NewActivity", back_populates="user_responses")
    participant = relationship("Participant", back_populates="user_responses")
