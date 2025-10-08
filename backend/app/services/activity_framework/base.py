"""Base Activity Abstract Class

Provides the abstract interface that all activity types must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID
from datetime import datetime


class BaseActivity(ABC):
    """Abstract base class for all activity types.

    All activity types must extend this class and implement the required methods.
    This ensures consistency across all activity implementations and provides
    a common interface for the framework to work with.
    """

    def __init__(self, activity_id: Optional[UUID], config: dict[str, Any]):
        """Initialize the activity with configuration.

        Args:
            activity_id: The UUID of the activity instance (None for new activities)
            config: The configuration dictionary for this activity
        """
        self.activity_id = activity_id
        self.config = config

    @abstractmethod
    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate the activity configuration.

        This method should check if the provided configuration is valid
        for this activity type.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """Return the JSON schema for activity configuration.

        This schema defines what configuration options are available
        for this activity type and their validation rules.

        Returns:
            JSON Schema dictionary defining valid configuration structure
        """
        pass

    @abstractmethod
    def process_response(
        self, participant_id: int, response_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process and validate a participant response.

        This method handles incoming responses from participants,
        validates them, and processes them for storage.

        Args:
            participant_id: ID of the participant submitting the response
            response_data: The response data submitted by the participant

        Returns:
            Processed response data ready for storage

        Raises:
            ValueError: If the response data is invalid
        """
        pass

    def can_transition_to(self, current_state: str, target_state: str) -> bool:
        """Check if activity can transition to target state.

        Override this method if the activity type has specific state
        transition rules beyond the default framework rules.

        Args:
            current_state: Current activity state
            target_state: Target state to transition to

        Returns:
            True if transition is allowed, False otherwise
        """
        # Default implementation allows all framework transitions
        return True

    def on_state_change(
        self, old_state: str, new_state: str, activity_data: dict[str, Any]
    ) -> None:
        """Handle state change events.

        Override this method to perform actions when the activity
        state changes (e.g., send notifications, update metadata).

        Args:
            old_state: Previous activity state
            new_state: New activity state
            activity_data: Current activity data
        """
        # Default implementation does nothing
        pass

    def get_default_metadata(self) -> dict[str, Any]:
        """Get default metadata for this activity type.

        Override this method to provide activity-type-specific
        default metadata values.

        Returns:
            Dictionary of default metadata values
        """
        return {
            "duration_seconds": None,
            "max_responses": None,
            "allow_multiple_responses": False,
            "show_live_results": True,
        }

    def calculate_results(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate aggregated results from responses.

        Override this method to provide activity-specific result
        calculation and aggregation logic.

        Args:
            responses: List of participant responses

        Returns:
            Dictionary containing calculated results
        """
        return {
            "total_responses": len(responses),
            "timestamp": datetime.utcnow().isoformat(),
        }
