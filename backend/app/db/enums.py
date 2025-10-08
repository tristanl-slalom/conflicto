"""Database enums for the application."""

from enum import Enum


class ActivityStatus(str, Enum):
    """Activity status enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityState(str, Enum):
    """Enhanced activity state enumeration for framework."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    EXPIRED = "expired"


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


# Deprecated - use ActivityType instead
class ActivityTypeEnum(str, Enum):
    """Activity type enumeration."""

    POLL = "poll"
    WORD_CLOUD = "word_cloud"
    QA = "qa"
    PLANNING_POKER = "planning_poker"
