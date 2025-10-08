"""Activity Registry

Manages registration and discovery of activity types.
"""

from typing import Any, Optional
from .base import BaseActivity


class ActivityTypeInfo:
    """Information about a registered activity type."""

    def __init__(
        self,
        activity_class: type[BaseActivity],
        schema: dict[str, Any],
        metadata: dict[str, Any],
    ):
        self.activity_class = activity_class
        self.schema = schema
        self.metadata = metadata


class ActivityRegistry:
    """Registry for activity types.

    This class manages the registration and discovery of activity types.
    All activity types must be registered here before they can be used.
    """

    _registry: dict[str, ActivityTypeInfo] = {}

    @classmethod
    def register(
        cls,
        activity_type: str,
        activity_class: type[BaseActivity],
        schema: dict[str, Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "1.0.0",
    ) -> None:
        """Register an activity type.

        Args:
            activity_type: Unique identifier for the activity type
            activity_class: The activity class that implements BaseActivity
            schema: JSON schema for activity configuration
            name: Human-readable name (defaults to formatted activity_type)
            description: Description of the activity type
            version: Version of the activity type

        Raises:
            ValueError: If activity type is already registered
        """
        if activity_type in cls._registry:
            raise ValueError(f"Activity type '{activity_type}' is already registered")

        if not issubclass(activity_class, BaseActivity):
            raise ValueError("Activity class must extend BaseActivity")

        metadata = {
            "id": activity_type,
            "name": name or activity_type.replace("_", " ").title(),
            "description": description or f"{activity_type} activity",
            "version": version,
        }

        cls._registry[activity_type] = ActivityTypeInfo(
            activity_class=activity_class, schema=schema, metadata=metadata
        )

    @classmethod
    def unregister(cls, activity_type: str) -> bool:
        """Unregister an activity type.

        Args:
            activity_type: Activity type to unregister

        Returns:
            True if activity type was unregistered, False if not found
        """
        if activity_type in cls._registry:
            del cls._registry[activity_type]
            return True
        return False

    @classmethod
    def get_activity_class(cls, activity_type: str) -> type[BaseActivity]:
        """Get activity class for type.

        Args:
            activity_type: Activity type identifier

        Returns:
            Activity class that implements BaseActivity

        Raises:
            ValueError: If activity type is not registered
        """
        if activity_type not in cls._registry:
            raise ValueError(f"Unknown activity type: {activity_type}")
        return cls._registry[activity_type].activity_class

    @classmethod
    def get_schema(cls, activity_type: str) -> dict[str, Any]:
        """Get JSON schema for activity type.

        Args:
            activity_type: Activity type identifier

        Returns:
            JSON schema for the activity configuration

        Raises:
            ValueError: If activity type is not registered
        """
        if activity_type not in cls._registry:
            raise ValueError(f"Unknown activity type: {activity_type}")
        return cls._registry[activity_type].schema

    @classmethod
    def get_metadata(cls, activity_type: str) -> dict[str, Any]:
        """Get metadata for activity type.

        Args:
            activity_type: Activity type identifier

        Returns:
            Metadata dictionary for the activity type

        Raises:
            ValueError: If activity type is not registered
        """
        if activity_type not in cls._registry:
            raise ValueError(f"Unknown activity type: {activity_type}")
        return cls._registry[activity_type].metadata

    @classmethod
    def get_all_types(cls) -> dict[str, dict[str, Any]]:
        """Get all registered activity types with their metadata.

        Returns:
            Dictionary mapping activity type IDs to their metadata
        """
        return {
            activity_type: info.metadata
            for activity_type, info in cls._registry.items()
        }

    @classmethod
    def get_all_schemas(cls) -> dict[str, dict[str, Any]]:
        """Get all registered activity types with their schemas.

        Returns:
            Dictionary mapping activity type IDs to their JSON schemas
        """
        return {
            activity_type: info.schema for activity_type, info in cls._registry.items()
        }

    @classmethod
    def is_registered(cls, activity_type: str) -> bool:
        """Check if activity type is registered.

        Args:
            activity_type: Activity type to check

        Returns:
            True if activity type is registered, False otherwise
        """
        return activity_type in cls._registry

    @classmethod
    def create_activity(
        cls, activity_type: str, activity_id: Optional[str], config: dict[str, Any]
    ) -> BaseActivity:
        """Create an activity instance.

        Args:
            activity_type: Type of activity to create
            activity_id: UUID of the activity (None for new activities)
            config: Configuration for the activity

        Returns:
            Instance of the activity class

        Raises:
            ValueError: If activity type is not registered
        """
        activity_class = cls.get_activity_class(activity_type)
        return activity_class(activity_id, config)

    @classmethod
    def clear_registry(cls) -> None:
        """Clear all registered activity types.

        This method is primarily intended for testing purposes.
        """
        cls._registry.clear()

    @classmethod
    def get_registry_info(cls) -> list[dict[str, Any]]:
        """Get detailed registry information for debugging.

        Returns:
            List of dictionaries containing detailed registry information
        """
        return [
            {
                "type": activity_type,
                "class": info.activity_class.__name__,
                "module": info.activity_class.__module__,
                "metadata": info.metadata,
                "schema_properties": list(info.schema.get("properties", {}).keys()),
            }
            for activity_type, info in cls._registry.items()
        ]
