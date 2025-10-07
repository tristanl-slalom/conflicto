"""Activity Status Enum for Activity model."""
import enum


class ActivityStatus(enum.Enum):
    """Activity status enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
