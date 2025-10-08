"""
SQLAlchemy models for the Caja application.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from app.db.enums import ActivityStatus, SessionStatus, ActivityType, ParticipantRole

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from app.db.database import Base


class JSONBType(TypeDecorator):
    """Database-agnostic JSONB type that works with both PostgreSQL and SQLite."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


class UUIDType(TypeDecorator):
    """Database-agnostic UUID type that works with both PostgreSQL and SQLite."""

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PGUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        else:
            # Convert UUID to string for SQLite
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        else:
            # Convert string back to UUID for SQLite
            from uuid import UUID

            return UUID(value)


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
    user_responses = relationship(
        "UserResponse", back_populates="session", cascade="all, delete-orphan"
    )


class Activity(Base):
    """Activity model with JSONB configuration storage."""

    __tablename__ = "activities"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE")
    )
    type: Mapped[str] = mapped_column(String(50))
    config: Mapped[dict] = mapped_column(JSONBType, default=dict)
    order_index: Mapped[int] = mapped_column(Integer)
    status: Mapped[ActivityStatus] = mapped_column(
        String(20), default=ActivityStatus.DRAFT
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    session = relationship("Session", back_populates="activities")
    user_responses = relationship(
        "UserResponse", back_populates="activity", cascade="all, delete-orphan"
    )


class Participant(Base):
    """Participant model representing users in a session."""

    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    nickname = Column(String(50), nullable=False)  # For QR code onboarding feature
    display_name = Column(String(100), nullable=True)  # For main branch compatibility
    role = Column(
        String(20), default="participant", nullable=False
    )  # For main branch compatibility
    is_active = Column(
        Boolean, default=True, nullable=False
    )  # For main branch compatibility
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    connection_data = Column(JSONBType, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("session_id", "nickname", name="unique_session_nickname"),
    )

    def __init__(self, **kwargs):
        # If display_name is provided but nickname is not, use display_name as nickname
        if "display_name" in kwargs and "nickname" not in kwargs:
            kwargs["nickname"] = kwargs["display_name"]
        # If nickname is provided but display_name is not, use nickname as display_name
        elif "nickname" in kwargs and "display_name" not in kwargs:
            kwargs["display_name"] = kwargs["nickname"]
        super().__init__(**kwargs)

    # Relationships
    session = relationship("Session", back_populates="participants")
    user_responses = relationship(
        "UserResponse", back_populates="participant", cascade="all, delete-orphan"
    )


class UserResponse(Base):
    """User Response model with JSONB response data storage."""

    __tablename__ = "user_responses"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE")
    )
    activity_id: Mapped[UUID] = mapped_column(
        UUIDType, ForeignKey("activities.id", ondelete="CASCADE")
    )
    participant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("participants.id", ondelete="CASCADE")
    )
    response_data: Mapped[dict] = mapped_column(JSONBType)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # Relationships
    session = relationship("Session", back_populates="user_responses")
    activity = relationship("Activity", back_populates="user_responses")
    participant = relationship("Participant", back_populates="user_responses")
