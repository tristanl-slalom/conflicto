"""Polling Activity Implementation

Polling/Survey activity that allows participants to vote on multiple choice questions.
"""

from typing import Any
from datetime import datetime
import logging

from app.services.activity_framework.base import BaseActivity

logger = logging.getLogger(__name__)


class PollingActivity(BaseActivity):
    """Polling/Survey activity implementation.

    Allows creating multiple choice polls where participants can select
    one or more options depending on configuration.
    """

    # JSON Schema for polling activity configuration
    SCHEMA = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "minLength": 1,
                "maxLength": 500,
                "description": "The poll question to display to participants",
            },
            "options": {
                "type": "array",
                "items": {"type": "string", "minLength": 1, "maxLength": 200},
                "minItems": 2,
                "maxItems": 10,
                "description": "List of answer options for participants to choose from",
            },
            "allow_multiple_choice": {
                "type": "boolean",
                "default": False,
                "description": "Whether participants can select multiple options",
            },
            "show_live_results": {
                "type": "boolean",
                "default": True,
                "description": "Whether to show live results to viewers",
            },
            "anonymous_voting": {
                "type": "boolean",
                "default": True,
                "description": "Whether voting is anonymous",
            },
        },
        "required": ["question", "options"],
        "additionalProperties": False,
    }

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate polling configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check required fields
            if "question" not in config:
                logger.warning("Polling config missing 'question' field")
                return False

            if "options" not in config:
                logger.warning("Polling config missing 'options' field")
                return False

            # Validate question
            question = config["question"]
            if not isinstance(question, str) or len(question.strip()) == 0:
                logger.warning("Polling question must be a non-empty string")
                return False

            if len(question) > 500:
                logger.warning(
                    "Polling question exceeds maximum length of 500 characters"
                )
                return False

            # Validate options
            options = config["options"]
            if not isinstance(options, list):
                logger.warning("Polling options must be a list")
                return False

            if len(options) < 2:
                logger.warning("Polling must have at least 2 options")
                return False

            if len(options) > 10:
                logger.warning("Polling cannot have more than 10 options")
                return False

            # Validate each option
            for i, option in enumerate(options):
                if not isinstance(option, str) or len(option.strip()) == 0:
                    logger.warning(f"Polling option {i} must be a non-empty string")
                    return False

                if len(option) > 200:
                    logger.warning(
                        f"Polling option {i} exceeds maximum length of 200 characters"
                    )
                    return False

            # Validate optional boolean fields
            bool_fields = [
                "allow_multiple_choice",
                "show_live_results",
                "anonymous_voting",
            ]
            for field in bool_fields:
                if field in config and not isinstance(config[field], bool):
                    logger.warning(f"Polling config field '{field}' must be boolean")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error validating polling config: {e}")
            return False

    def get_schema(self) -> dict[str, Any]:
        """Return JSON schema for polling configuration.

        Returns:
            JSON Schema dictionary
        """
        return self.SCHEMA

    def process_response(
        self, participant_id: int, response_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process polling response from participant.

        Args:
            participant_id: ID of the participant submitting the response
            response_data: Response data containing selected options

        Returns:
            Processed response data ready for storage

        Raises:
            ValueError: If response data is invalid
        """
        try:
            # Extract selected options
            selected_options = response_data.get("selected_options", [])

            # Validate response format
            if not isinstance(selected_options, list):
                raise ValueError("Response must contain 'selected_options' as a list")

            # Validate selected options against configuration
            valid_options = self.config.get("options", [])
            if not valid_options:
                raise ValueError("Activity configuration has no valid options")

            # Check that all selected options are valid
            for option in selected_options:
                if option not in valid_options:
                    raise ValueError(f"Invalid option selected: '{option}'")

            # Check multiple choice rules
            allow_multiple = self.config.get("allow_multiple_choice", False)
            if not allow_multiple and len(selected_options) > 1:
                raise ValueError("Multiple choices not allowed for this poll")

            # Validate at least one option selected
            if len(selected_options) == 0:
                raise ValueError("At least one option must be selected")

            # Create processed response
            processed_response = {
                "type": "poll_response",
                "participant_id": participant_id,
                "selected_options": selected_options,
                "timestamp": datetime.utcnow().isoformat(),
                "anonymous": self.config.get("anonymous_voting", True),
            }

            # Add participant info if not anonymous
            if not self.config.get("anonymous_voting", True):
                processed_response["participant_info"] = {
                    "id": participant_id,
                    # Additional participant info could be added here
                }

            return processed_response

        except Exception as e:
            logger.error(f"Error processing polling response: {e}")
            raise ValueError(f"Failed to process polling response: {str(e)}")

    def calculate_results(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate aggregated polling results.

        Args:
            responses: List of participant responses

        Returns:
            Dictionary containing calculated results with vote counts
        """
        try:
            # Initialize vote counts for all options
            options = self.config.get("options", [])
            vote_counts = {option: 0 for option in options}

            # Count votes from responses
            total_responses = 0
            response_timestamps = []

            for response in responses:
                response_data = response.get("response_data", {})
                selected_options = response_data.get("selected_options", [])

                # Count votes for each selected option
                for option in selected_options:
                    if option in vote_counts:
                        vote_counts[option] += 1

                total_responses += 1

                # Track response timing
                if "timestamp" in response_data:
                    response_timestamps.append(response_data["timestamp"])

            # Calculate percentages
            percentages = {}
            if total_responses > 0:
                for option, count in vote_counts.items():
                    percentages[option] = round((count / total_responses) * 100, 1)
            else:
                percentages = {option: 0.0 for option in options}

            # Find most popular option(s)
            max_votes = max(vote_counts.values()) if vote_counts.values() else 0
            most_popular = [
                option for option, count in vote_counts.items() if count == max_votes
            ]

            return {
                "type": "poll_results",
                "question": self.config.get("question", ""),
                "options": options,
                "vote_counts": vote_counts,
                "percentages": percentages,
                "total_responses": total_responses,
                "most_popular": most_popular,
                "allow_multiple_choice": self.config.get(
                    "allow_multiple_choice", False
                ),
                "show_live_results": self.config.get("show_live_results", True),
                "last_updated": datetime.utcnow().isoformat(),
                "response_timestamps": response_timestamps,
            }

        except Exception as e:
            logger.error(f"Error calculating polling results: {e}")
            return {
                "type": "poll_results",
                "error": f"Failed to calculate results: {str(e)}",
                "total_responses": len(responses),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def get_default_metadata(self) -> dict[str, Any]:
        """Get default metadata for polling activities.

        Returns:
            Dictionary of default metadata values
        """
        return {
            "duration_seconds": 300,  # 5 minutes default
            "max_responses": None,  # No limit by default
            "allow_multiple_responses": False,  # One response per participant
            "show_live_results": True,
            "activity_type": "poll",
            "requires_moderation": False,
        }

    def can_transition_to(self, current_state: str, target_state: str) -> bool:
        """Check if polling activity can transition to target state.

        Polling activities can use all default state transitions.

        Args:
            current_state: Current activity state
            target_state: Target state to transition to

        Returns:
            True (polling activities support all default transitions)
        """
        return True

    def on_state_change(
        self, old_state: str, new_state: str, activity_data: dict[str, Any]
    ) -> None:
        """Handle polling activity state changes.

        Args:
            old_state: Previous activity state
            new_state: New activity state
            activity_data: Current activity data
        """
        logger.info(
            f"Polling activity {self.activity_id} transitioned from {old_state} to {new_state}"
        )

        # Log transition for analytics
        if new_state == "active":
            logger.info(
                f"Polling activity {self.activity_id} started: '{self.config.get('question', 'Unknown')}'"
            )
        elif new_state == "expired":
            logger.info(f"Polling activity {self.activity_id} ended")
