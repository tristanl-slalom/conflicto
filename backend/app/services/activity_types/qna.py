"""Q&A Activity Implementation

Q&A activity that allows participants to submit questions and vote on them.
"""

from typing import Any
from datetime import datetime
import logging

from app.services.activity_framework.base import BaseActivity

logger = logging.getLogger(__name__)


class QnaActivity(BaseActivity):
    """Q&A activity implementation.

    Allows participants to submit questions and vote on questions
    submitted by others. Supports moderation and anonymous submissions.
    """

    # JSON Schema for Q&A activity configuration
    SCHEMA = {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200,
                "description": "The topic or theme for the Q&A session",
            },
            "allow_anonymous": {
                "type": "boolean",
                "default": True,
                "description": "Whether participants can submit questions anonymously",
            },
            "enable_voting": {
                "type": "boolean",
                "default": True,
                "description": "Whether participants can vote on questions",
            },
            "moderate_questions": {
                "type": "boolean",
                "default": False,
                "description": "Whether questions require moderation before being visible",
            },
            "max_question_length": {
                "type": "integer",
                "minimum": 10,
                "maximum": 1000,
                "default": 500,
                "description": "Maximum length for submitted questions",
            },
            "allow_multiple_votes": {
                "type": "boolean",
                "default": False,
                "description": "Whether participants can vote on multiple questions",
            },
            "show_vote_counts": {
                "type": "boolean",
                "default": True,
                "description": "Whether to display vote counts to participants",
            },
        },
        "required": ["topic"],
        "additionalProperties": False,
    }

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate Q&A configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check required fields
            if "topic" not in config:
                logger.warning("Q&A config missing 'topic' field")
                return False

            # Validate topic
            topic = config["topic"]
            if not isinstance(topic, str) or len(topic.strip()) == 0:
                logger.warning("Q&A topic must be a non-empty string")
                return False

            if len(topic) > 200:
                logger.warning("Q&A topic exceeds maximum length of 200 characters")
                return False

            # Validate optional boolean fields
            bool_fields = [
                "allow_anonymous",
                "enable_voting",
                "moderate_questions",
                "allow_multiple_votes",
                "show_vote_counts",
            ]
            for field in bool_fields:
                if field in config and not isinstance(config[field], bool):
                    logger.warning(f"Q&A config field '{field}' must be boolean")
                    return False

            # Validate max_question_length
            if "max_question_length" in config:
                max_length = config["max_question_length"]
                if (
                    not isinstance(max_length, int)
                    or max_length < 10
                    or max_length > 1000
                ):
                    logger.warning(
                        "Q&A max_question_length must be integer between 10 and 1000"
                    )
                    return False

            return True
        except Exception as e:
            logger.error(f"Error validating Q&A config: {e}")
            return False

    def get_schema(self) -> dict[str, Any]:
        """Return JSON schema for Q&A configuration.

        Returns:
            JSON Schema dictionary
        """
        return self.SCHEMA

    def process_response(
        self, participant_id: int, response_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process Q&A response from participant.

        Args:
            participant_id: ID of the participant submitting the response
            response_data: Response data containing question submission or vote

        Returns:
            Processed response data ready for storage

        Raises:
            ValueError: If response data is invalid
        """
        try:
            response_type = response_data.get("type")

            if response_type == "question":
                return self._process_question_submission(participant_id, response_data)
            elif response_type == "vote":
                return self._process_vote(participant_id, response_data)
            else:
                raise ValueError(
                    f"Invalid response type: {response_type}. Must be 'question' or 'vote'"
                )

        except Exception as e:
            logger.error(f"Error processing Q&A response: {e}")
            raise ValueError(f"Failed to process Q&A response: {str(e)}")

    def _process_question_submission(
        self, participant_id: int, response_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a question submission.

        Args:
            participant_id: ID of the participant
            response_data: Response data containing the question

        Returns:
            Processed question submission
        """
        question_text = response_data.get("question_text", "").strip()

        # Validate question text
        if not question_text:
            raise ValueError("Question text cannot be empty")

        max_length = self.config.get("max_question_length", 500)
        if len(question_text) > max_length:
            raise ValueError(
                f"Question exceeds maximum length of {max_length} characters"
            )

        # Check if anonymous submissions are allowed
        is_anonymous = response_data.get(
            "anonymous", self.config.get("allow_anonymous", True)
        )
        if is_anonymous and not self.config.get("allow_anonymous", True):
            raise ValueError("Anonymous question submissions are not allowed")

        # Generate unique question ID (timestamp-based for now)
        question_id = f"q_{int(datetime.utcnow().timestamp() * 1000)}_{participant_id}"

        processed_response = {
            "type": "question",
            "question_id": question_id,
            "participant_id": participant_id,
            "question_text": question_text,
            "anonymous": is_anonymous,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending"
            if self.config.get("moderate_questions", False)
            else "approved",
            "vote_count": 0,
            "voters": [],
        }

        return processed_response

    def _process_vote(
        self, participant_id: int, response_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a vote on a question.

        Args:
            participant_id: ID of the participant
            response_data: Response data containing the vote

        Returns:
            Processed vote
        """
        question_id = response_data.get("question_id")
        if not question_id:
            raise ValueError("Vote must specify question_id")

        # Check if voting is enabled
        if not self.config.get("enable_voting", True):
            raise ValueError("Voting is not enabled for this Q&A session")

        processed_response = {
            "type": "vote",
            "participant_id": participant_id,
            "question_id": question_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return processed_response

    def calculate_results(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate aggregated Q&A results.

        Args:
            responses: List of participant responses

        Returns:
            Dictionary containing calculated results with questions and votes
        """
        try:
            questions = {}
            votes = {}

            # Process all responses to build questions and votes
            for response in responses:
                response_data = response.get("response_data", {})
                response_type = response_data.get("type")

                if response_type == "question":
                    question_id = response_data.get("question_id")
                    if question_id:
                        questions[question_id] = {
                            "id": question_id,
                            "text": response_data.get("question_text", ""),
                            "anonymous": response_data.get("anonymous", True),
                            "participant_id": response_data.get("participant_id"),
                            "timestamp": response_data.get("timestamp"),
                            "status": response_data.get("status", "approved"),
                            "vote_count": 0,
                            "voters": [],
                        }

                elif response_type == "vote":
                    question_id = response_data.get("question_id")
                    participant_id = response_data.get("participant_id")
                    if question_id and participant_id:
                        if question_id not in votes:
                            votes[question_id] = []
                        votes[question_id].append(
                            {
                                "participant_id": participant_id,
                                "timestamp": response_data.get("timestamp"),
                            }
                        )

            # Apply votes to questions
            for question_id, question_votes in votes.items():
                if question_id in questions:
                    # Handle multiple votes logic
                    if self.config.get("allow_multiple_votes", False):
                        # Count all votes
                        questions[question_id]["vote_count"] = len(question_votes)
                        questions[question_id]["voters"] = [
                            v["participant_id"] for v in question_votes
                        ]
                    else:
                        # Count unique voters only
                        unique_voters = list(
                            set(v["participant_id"] for v in question_votes)
                        )
                        questions[question_id]["vote_count"] = len(unique_voters)
                        questions[question_id]["voters"] = unique_voters

            # Sort questions by vote count (most popular first)
            sorted_questions = sorted(
                questions.values(), key=lambda q: q["vote_count"], reverse=True
            )

            # Filter approved questions only for public display
            approved_questions = [
                q for q in sorted_questions if q.get("status") == "approved"
            ]
            pending_questions = [
                q for q in sorted_questions if q.get("status") == "pending"
            ]

            return {
                "type": "qna_results",
                "topic": self.config.get("topic", ""),
                "total_questions": len(questions),
                "total_votes": sum(len(v) for v in votes.values()),
                "approved_questions": approved_questions,
                "pending_questions": pending_questions
                if not self.config.get("moderate_questions", False)
                else [],
                "most_popular_question": approved_questions[0]
                if approved_questions
                else None,
                "enable_voting": self.config.get("enable_voting", True),
                "show_vote_counts": self.config.get("show_vote_counts", True),
                "allow_anonymous": self.config.get("allow_anonymous", True),
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error calculating Q&A results: {e}")
            return {
                "type": "qna_results",
                "error": f"Failed to calculate results: {str(e)}",
                "total_responses": len(responses),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def get_default_metadata(self) -> dict[str, Any]:
        """Get default metadata for Q&A activities.

        Returns:
            Dictionary of default metadata values
        """
        return {
            "duration_seconds": 900,  # 15 minutes default
            "max_responses": None,  # No limit by default
            "allow_multiple_responses": True,  # Can submit questions and votes
            "show_live_results": True,
            "activity_type": "qna",
            "requires_moderation": True,  # Q&A often needs moderation
        }

    def can_transition_to(self, current_state: str, target_state: str) -> bool:
        """Check if Q&A activity can transition to target state.

        Q&A activities can use all default state transitions.

        Args:
            current_state: Current activity state
            target_state: Target state to transition to

        Returns:
            True (Q&A activities support all default transitions)
        """
        return True

    def on_state_change(
        self, old_state: str, new_state: str, activity_data: dict[str, Any]
    ) -> None:
        """Handle Q&A activity state changes.

        Args:
            old_state: Previous activity state
            new_state: New activity state
            activity_data: Current activity data
        """
        logger.info(
            f"Q&A activity {self.activity_id} transitioned from {old_state} to {new_state}"
        )

        # Log transition for analytics
        if new_state == "active":
            logger.info(
                f"Q&A session {self.activity_id} started: '{self.config.get('topic', 'Unknown')}'"
            )
        elif new_state == "expired":
            logger.info(f"Q&A session {self.activity_id} ended")
