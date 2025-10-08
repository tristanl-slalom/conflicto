"""Activity State Machine

Manages activity state transitions and validation.
"""

from typing import Optional, Any
from datetime import datetime, timedelta
import logging

from app.db.enums import ActivityState

logger = logging.getLogger(__name__)


class ActivityStateMachine:
    """Manages activity state transitions.

    This class provides a centralized way to manage activity state changes
    with proper validation and business rule enforcement.
    """

    # Valid state transitions mapping
    TRANSITIONS: dict[ActivityState, list[ActivityState]] = {
        ActivityState.DRAFT: [ActivityState.PUBLISHED],
        ActivityState.PUBLISHED: [ActivityState.ACTIVE, ActivityState.DRAFT],
        ActivityState.ACTIVE: [ActivityState.EXPIRED],
        ActivityState.EXPIRED: [],  # Terminal state
    }

    @classmethod
    def can_transition(cls, current_state: str, target_state: str) -> bool:
        """Check if transition from current state to target state is valid.

        Args:
            current_state: Current activity state
            target_state: Target state to transition to

        Returns:
            True if transition is valid, False otherwise
        """
        try:
            current_enum = ActivityState(current_state)
            target_enum = ActivityState(target_state)
            return target_enum in cls.TRANSITIONS.get(current_enum, [])
        except ValueError:
            # Invalid state value
            return False

    @classmethod
    def get_valid_transitions(cls, current_state: str) -> list[str]:
        """Get list of valid target states from current state.

        Args:
            current_state: Current activity state

        Returns:
            List of valid target state strings
        """
        try:
            current_enum = ActivityState(current_state)
            return [state.value for state in cls.TRANSITIONS.get(current_enum, [])]
        except ValueError:
            return []

    @classmethod
    def transition(
        cls,
        activity: Any,  # Activity model instance
        target_state: str,
        reason: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """Perform state transition on activity.

        Args:
            activity: SQLAlchemy Activity model instance
            target_state: Target state to transition to
            reason: Optional reason for the transition
            force: If True, skip validation (use with caution)

        Returns:
            True if transition was successful, False otherwise
        """
        if not force and not cls.can_transition(activity.state, target_state):
            logger.warning(
                "Invalid state transition attempted: %s -> %s for activity %s",
                activity.state,
                target_state,
                activity.id,
            )
            return False

        old_state = activity.state
        activity.state = target_state
        activity.updated_at = datetime.utcnow()

        # Handle state-specific logic
        cls._handle_state_transition(activity, old_state, target_state, reason)

        if reason:
            logger.info(
                "Activity %s transitioned from %s to %s (reason: %s)",
                activity.id,
                old_state,
                target_state,
                reason,
            )
        else:
            logger.info(
                "Activity %s transitioned from %s to %s",
                activity.id,
                old_state,
                target_state,
            )

        return True

    @classmethod
    def _handle_state_transition(
        cls, activity: Any, old_state: str, new_state: str, reason: Optional[str]
    ) -> None:
        """Handle state transition side effects.

        Args:
            activity: Activity model instance
            old_state: Previous state
            new_state: New state
            reason: Optional reason for transition
        """
        # Handle ACTIVE state logic
        if new_state == ActivityState.ACTIVE:
            cls._handle_activation(activity)

        # Handle EXPIRED state logic
        elif new_state == ActivityState.EXPIRED:
            cls._handle_expiration(activity)

    @classmethod
    def _handle_activation(cls, activity: Any) -> None:
        """Handle activity activation.

        Args:
            activity: Activity model instance
        """
        # Set expiration time if duration is specified
        duration_seconds = activity.activity_metadata.get("duration_seconds")
        if duration_seconds:
            activity.expires_at = datetime.utcnow() + timedelta(
                seconds=duration_seconds
            )
            logger.info(f"Activity {activity.id} will expire at {activity.expires_at}")

    @classmethod
    def _handle_expiration(cls, activity: Any) -> None:
        """Handle activity expiration.

        Args:
            activity: Activity model instance
        """
        # Mark expiration time if not already set
        if not activity.expires_at:
            activity.expires_at = datetime.utcnow()
            logger.info(f"Activity {activity.id} expired at {activity.expires_at}")

    @classmethod
    def check_expired_activities(cls, activities: list[Any]) -> list[Any]:
        """Check for activities that should be automatically expired.

        This method can be called periodically to automatically transition
        activities that have reached their expiration time.

        Args:
            activities: List of active activities to check

        Returns:
            List of activities that were transitioned to expired state
        """
        expired_activities = []
        current_time = datetime.utcnow()

        for activity in activities:
            if (
                activity.state == ActivityState.ACTIVE
                and activity.expires_at
                and current_time >= activity.expires_at
            ):
                if cls.transition(
                    activity, ActivityState.EXPIRED, "Automatic expiration"
                ):
                    expired_activities.append(activity)

        return expired_activities

    @classmethod
    def validate_state_transition_request(
        cls,
        current_state: str,
        target_state: str,
        activity_type: str,
        activity_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate a state transition request with detailed feedback.

        Args:
            current_state: Current activity state
            target_state: Requested target state
            activity_type: Type of activity
            activity_config: Activity configuration

        Returns:
            Dictionary with validation results and error messages
        """
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
        }

        # Check basic state transition validity
        if not cls.can_transition(current_state, target_state):
            result["errors"].append(
                f"Invalid state transition: {current_state} -> {target_state}"
            )
            return result

        # Check state-specific requirements
        if target_state == ActivityState.ACTIVE:
            validation_result = cls._validate_activation_requirements(activity_config)
            result["errors"].extend(validation_result.get("errors", []))
            result["warnings"].extend(validation_result.get("warnings", []))

        result["valid"] = len(result["errors"]) == 0
        return result

    @classmethod
    def _validate_activation_requirements(
        cls, activity_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate requirements for activating an activity.

        Args:
            activity_config: Activity configuration to validate

        Returns:
            Dictionary with validation errors and warnings
        """
        errors = []
        warnings = []

        # Example validation: Check if required configuration is present
        # This can be extended based on specific activity requirements

        return {
            "errors": errors,
            "warnings": warnings,
        }

    @classmethod
    def get_state_info(cls) -> dict[str, Any]:
        """Get information about available states and transitions.

        Returns:
            Dictionary containing state machine information
        """
        return {
            "states": [state.value for state in ActivityState],
            "transitions": {
                state.value: [target.value for target in targets]
                for state, targets in cls.TRANSITIONS.items()
            },
            "terminal_states": [
                state.value for state, targets in cls.TRANSITIONS.items() if not targets
            ],
        }
