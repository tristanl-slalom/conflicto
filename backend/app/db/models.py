"""
SQLAlchemy models for the Caja application.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    activities = relationship("Activity", back_populates="session", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="session", cascade="all, delete-orphan")


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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="activities")
    responses = relationship("ActivityResponse", back_populates="activity", cascade="all, delete-orphan")


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
    responses = relationship("ActivityResponse", back_populates="participant", cascade="all, delete-orphan")


class ActivityResponse(Base):
    """Activity response model for storing participant responses."""
    
    __tablename__ = "activity_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    response_data = Column(JSON, nullable=False)  # Store response content
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    activity = relationship("Activity", back_populates="responses")
    participant = relationship("Participant", back_populates="responses")