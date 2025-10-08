"""Word Cloud Activity Implementation

Word Cloud activity that allows participants to submit words or phrases
that get aggregated and displayed as a word cloud visualization.
"""

from typing import Any
from datetime import datetime
import logging
import re
from collections import Counter

from app.services.activity_framework.base import BaseActivity

logger = logging.getLogger(__name__)


class WordCloudActivity(BaseActivity):
    """Word Cloud activity implementation.

    Allows participants to submit words or short phrases that are
    aggregated and can be displayed as a word cloud visualization.
    """

    # JSON Schema for Word Cloud activity configuration
    SCHEMA = {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "minLength": 1,
                "maxLength": 300,
                "description": "The prompt or question to guide word submissions",
            },
            "max_word_length": {
                "type": "integer",
                "minimum": 3,
                "maximum": 50,
                "default": 20,
                "description": "Maximum length for individual words",
            },
            "max_words_per_submission": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "default": 3,
                "description": "Maximum number of words per submission",
            },
            "allow_phrases": {
                "type": "boolean",
                "default": False,
                "description": "Whether to allow multi-word phrases",
            },
            "moderate_submissions": {
                "type": "boolean",
                "default": True,
                "description": "Whether submissions require moderation",
            },
            "case_sensitive": {
                "type": "boolean",
                "default": False,
                "description": "Whether word matching is case sensitive",
            },
            "show_live_results": {
                "type": "boolean",
                "default": True,
                "description": "Whether to show live word cloud updates",
            },
            "banned_words": {
                "type": "array",
                "items": {"type": "string", "minLength": 1, "maxLength": 50},
                "default": [],
                "description": "List of banned/filtered words",
            },
        },
        "required": ["prompt"],
        "additionalProperties": False,
    }

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate Word Cloud configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check required fields
            if "prompt" not in config:
                logger.warning("Word Cloud config missing 'prompt' field")
                return False

            # Validate prompt
            prompt = config["prompt"]
            if not isinstance(prompt, str) or len(prompt.strip()) == 0:
                logger.warning("Word Cloud prompt must be a non-empty string")
                return False

            if len(prompt) > 300:
                logger.warning(
                    "Word Cloud prompt exceeds maximum length of 300 characters"
                )
                return False

            # Validate integer fields
            int_fields = {
                "max_word_length": (3, 50, 20),
                "max_words_per_submission": (1, 10, 3),
            }
            for field, (min_val, max_val, default) in int_fields.items():
                if field in config:
                    value = config[field]
                    if not isinstance(value, int) or value < min_val or value > max_val:
                        logger.warning(
                            f"Word Cloud {field} must be integer between {min_val} and {max_val}"
                        )
                        return False

            # Validate boolean fields
            bool_fields = [
                "allow_phrases",
                "moderate_submissions",
                "case_sensitive",
                "show_live_results",
            ]
            for field in bool_fields:
                if field in config and not isinstance(config[field], bool):
                    logger.warning(f"Word Cloud config field '{field}' must be boolean")
                    return False

            # Validate banned words
            if "banned_words" in config:
                banned_words = config["banned_words"]
                if not isinstance(banned_words, list):
                    logger.warning("Word Cloud banned_words must be a list")
                    return False

                for word in banned_words:
                    if not isinstance(word, str) or len(word.strip()) == 0:
                        logger.warning(
                            "Word Cloud banned words must be non-empty strings"
                        )
                        return False

            return True
        except Exception as e:
            logger.error(f"Error validating Word Cloud config: {e}")
            return False

    def get_schema(self) -> dict[str, Any]:
        """Return JSON schema for Word Cloud configuration.

        Returns:
            JSON Schema dictionary
        """
        return self.SCHEMA

    def process_response(
        self, participant_id: int, response_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process Word Cloud response from participant.

        Args:
            participant_id: ID of the participant submitting words
            response_data: Response data containing submitted words

        Returns:
            Processed response data ready for storage

        Raises:
            ValueError: If response data is invalid
        """
        try:
            # Extract submitted words
            words = response_data.get("words", [])

            if not isinstance(words, list):
                raise ValueError("Response must contain 'words' as a list")

            if len(words) == 0:
                raise ValueError("At least one word must be submitted")

            # Validate number of words
            max_words = self.config.get("max_words_per_submission", 3)
            if len(words) > max_words:
                raise ValueError(f"Maximum {max_words} words allowed per submission")

            # Process and validate each word
            processed_words = []
            for word in words:
                processed_word = self._process_word(word)
                if processed_word:
                    processed_words.append(processed_word)

            if not processed_words:
                raise ValueError("No valid words found after processing")

            processed_response = {
                "type": "word_submission",
                "participant_id": participant_id,
                "words": processed_words,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "pending"
                if self.config.get("moderate_submissions", True)
                else "approved",
            }

            return processed_response

        except Exception as e:
            logger.error(f"Error processing Word Cloud response: {e}")
            raise ValueError(f"Failed to process Word Cloud response: {str(e)}")

    def _process_word(self, word: str) -> str:
        """Process and validate a single word.

        Args:
            word: Raw word submission

        Returns:
            Processed word or None if invalid
        """
        if not isinstance(word, str):
            raise ValueError("Each word must be a string")

        # Clean and normalize the word
        cleaned_word = word.strip()
        if not self.config.get("case_sensitive", False):
            cleaned_word = cleaned_word.lower()

        # Remove extra whitespace and special characters
        cleaned_word = re.sub(r"\s+", " ", cleaned_word)
        cleaned_word = re.sub(r"[^\w\s-]", "", cleaned_word)

        if not cleaned_word:
            raise ValueError(f"Word '{word}' becomes empty after cleaning")

        # Validate word length
        max_length = self.config.get("max_word_length", 20)
        if len(cleaned_word) > max_length:
            raise ValueError(
                f"Word '{word}' exceeds maximum length of {max_length} characters"
            )

        # Check for phrases
        if not self.config.get("allow_phrases", False) and " " in cleaned_word:
            raise ValueError(f"Phrases not allowed: '{word}'")

        # Check banned words
        banned_words = [w.lower() for w in self.config.get("banned_words", [])]
        check_word = cleaned_word.lower()
        if check_word in banned_words:
            raise ValueError(f"Word '{word}' is not allowed")

        return cleaned_word

    def calculate_results(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate aggregated Word Cloud results.

        Args:
            responses: List of participant responses

        Returns:
            Dictionary containing word frequencies and cloud data
        """
        try:
            all_words = []
            word_frequencies = Counter()
            participant_count = 0
            submission_timestamps = []

            # Process all responses to collect words
            for response in responses:
                response_data = response.get("response_data", {})

                if response_data.get("type") == "word_submission":
                    status = response_data.get("status", "approved")

                    # Only include approved submissions in results
                    if status == "approved":
                        words = response_data.get("words", [])
                        all_words.extend(words)

                        # Count frequency of each word
                        for word in words:
                            word_frequencies[word] += 1

                        participant_count += 1

                        if "timestamp" in response_data:
                            submission_timestamps.append(response_data["timestamp"])

            # Get most common words
            most_common = word_frequencies.most_common(50)  # Top 50 words

            # Create word cloud data with relative sizes
            max_frequency = max(word_frequencies.values()) if word_frequencies else 1
            word_cloud_data = [
                {
                    "word": word,
                    "frequency": frequency,
                    "size": min(
                        100, max(10, int((frequency / max_frequency) * 100))
                    ),  # Size 10-100
                    "percentage": round((frequency / len(all_words)) * 100, 1)
                    if all_words
                    else 0,
                }
                for word, frequency in most_common
            ]

            # Get unique word count
            unique_words = len(word_frequencies)
            total_submissions = len(all_words)

            return {
                "type": "word_cloud_results",
                "prompt": self.config.get("prompt", ""),
                "word_cloud_data": word_cloud_data,
                "word_frequencies": dict(word_frequencies),
                "most_common_words": most_common[:10],  # Top 10
                "unique_word_count": unique_words,
                "total_word_submissions": total_submissions,
                "participant_count": participant_count,
                "show_live_results": self.config.get("show_live_results", True),
                "allow_phrases": self.config.get("allow_phrases", False),
                "last_updated": datetime.utcnow().isoformat(),
                "submission_timestamps": submission_timestamps,
            }

        except Exception as e:
            logger.error(f"Error calculating Word Cloud results: {e}")
            return {
                "type": "word_cloud_results",
                "error": f"Failed to calculate results: {str(e)}",
                "total_responses": len(responses),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def get_default_metadata(self) -> dict[str, Any]:
        """Get default metadata for Word Cloud activities.

        Returns:
            Dictionary of default metadata values
        """
        return {
            "duration_seconds": 600,  # 10 minutes default
            "max_responses": 100,  # Reasonable limit for word clouds
            "allow_multiple_responses": True,  # Can submit multiple times
            "show_live_results": True,
            "activity_type": "word_cloud",
            "requires_moderation": True,  # Word clouds often need moderation
        }

    def can_transition_to(self, current_state: str, target_state: str) -> bool:
        """Check if Word Cloud activity can transition to target state.

        Word Cloud activities can use all default state transitions.

        Args:
            current_state: Current activity state
            target_state: Target state to transition to

        Returns:
            True (Word Cloud activities support all default transitions)
        """
        return True

    def on_state_change(
        self, old_state: str, new_state: str, activity_data: dict[str, Any]
    ) -> None:
        """Handle Word Cloud activity state changes.

        Args:
            old_state: Previous activity state
            new_state: New activity state
            activity_data: Current activity data
        """
        logger.info(
            f"Word Cloud activity {self.activity_id} transitioned from {old_state} to {new_state}"
        )

        # Log transition for analytics
        if new_state == "active":
            logger.info(
                f"Word Cloud activity {self.activity_id} started: '{self.config.get('prompt', 'Unknown')}'"
            )
        elif new_state == "expired":
            logger.info(f"Word Cloud activity {self.activity_id} ended")
