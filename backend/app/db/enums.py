"""Database enums for the application."""
import enum


class ActivityStatus(enum.Enum):
    """Activity status enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityTypeEnum(enum.Enum):
    """Activity type enumeration."""
    POLL = "poll"
    WORD_CLOUD = "word_cloud"
    QA = "qa"
    PLANNING_POKER = "planning_poker"
