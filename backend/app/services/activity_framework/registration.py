"""Activity Type Registration System

Registers all available activity types at application startup.
"""

import logging
from typing import Any

from app.services.activity_framework.registry import ActivityRegistry
from app.services.activity_types.polling import PollingActivity
from app.services.activity_types.qna import QnaActivity
from app.services.activity_types.word_cloud import WordCloudActivity

logger = logging.getLogger(__name__)


def register_activity_types() -> None:
    """Register all activity types at startup.

    This function should be called during application initialization
    to register all available activity types with the framework.
    """
    try:
        logger.info("Registering activity types...")

        # Register Polling Activity
        ActivityRegistry.register(
            activity_type="poll",
            activity_class=PollingActivity,
            schema=PollingActivity.SCHEMA,
            name="Polling",
            description="Multiple choice polls and surveys where participants vote on options",
            version="1.0.0",
        )
        logger.info("Registered activity type: poll")

        # Register Q&A Activity
        ActivityRegistry.register(
            activity_type="qna",
            activity_class=QnaActivity,
            schema=QnaActivity.SCHEMA,
            name="Q&A Session",
            description="Question and answer sessions where participants submit and vote on questions",
            version="1.0.0",
        )
        logger.info("Registered activity type: qna")

        # Register Word Cloud Activity
        ActivityRegistry.register(
            activity_type="word_cloud",
            activity_class=WordCloudActivity,
            schema=WordCloudActivity.SCHEMA,
            name="Word Cloud",
            description="Collect words and phrases from participants to create word cloud visualizations",
            version="1.0.0",
        )
        logger.info("Registered activity type: word_cloud")

        # Log registration summary
        registered_types = ActivityRegistry.get_all_types()
        logger.info(
            f"Activity type registration complete. Registered {len(registered_types)} types: {list(registered_types.keys())}"
        )

        # Validate all registrations
        _validate_registrations()

    except Exception as e:
        logger.error(f"Failed to register activity types: {e}")
        raise


def _validate_registrations() -> None:
    """Validate that all activity type registrations are correct.

    This performs basic validation to ensure all registered activity types
    have the required components and can be instantiated correctly.
    """
    try:
        registered_types = ActivityRegistry.get_all_types()

        for activity_type in registered_types.keys():
            # Test that we can get the activity class
            activity_class = ActivityRegistry.get_activity_class(activity_type)

            # Test that we can get the schema
            schema = ActivityRegistry.get_schema(activity_type)

            # Test that we can create an instance with empty config
            try:
                instance = ActivityRegistry.create_activity(activity_type, None, {})
                # Test that the instance has the required methods
                assert hasattr(
                    instance, "validate_config"
                ), f"Activity {activity_type} missing validate_config method"
                assert hasattr(
                    instance, "get_schema"
                ), f"Activity {activity_type} missing get_schema method"
                assert hasattr(
                    instance, "process_response"
                ), f"Activity {activity_type} missing process_response method"

                logger.debug(f"Activity type {activity_type} validated successfully")
            except Exception as e:
                logger.warning(f"Activity type {activity_type} validation warning: {e}")

        logger.info(
            f"All {len(registered_types)} activity type registrations validated"
        )

    except Exception as e:
        logger.error(f"Activity type registration validation failed: {e}")
        raise


def get_registration_info() -> dict[str, Any]:
    """Get detailed information about registered activity types.

    Returns:
        Dictionary containing registration information for debugging
    """
    try:
        registered_types = ActivityRegistry.get_all_types()
        registry_info = ActivityRegistry.get_registry_info()

        return {
            "total_registered": len(registered_types),
            "registered_types": list(registered_types.keys()),
            "type_metadata": registered_types,
            "registry_details": registry_info,
        }
    except Exception as e:
        logger.error(f"Failed to get registration info: {e}")
        return {
            "error": str(e),
            "total_registered": 0,
        }


def clear_registrations() -> None:
    """Clear all activity type registrations.

    This function is primarily intended for testing purposes
    to reset the registry state.
    """
    logger.warning("Clearing all activity type registrations")
    ActivityRegistry.clear_registry()


# Convenience function for testing individual activity types
def test_activity_type(activity_type: str) -> dict[str, Any]:
    """Test a specific activity type registration.

    Args:
        activity_type: Activity type to test

    Returns:
        Test results dictionary
    """
    try:
        if not ActivityRegistry.is_registered(activity_type):
            return {
                "success": False,
                "error": f"Activity type '{activity_type}' is not registered",
            }

        # Get activity class and schema
        activity_class = ActivityRegistry.get_activity_class(activity_type)
        schema = ActivityRegistry.get_schema(activity_type)
        metadata = ActivityRegistry.get_metadata(activity_type)

        # Try to create instance
        instance = ActivityRegistry.create_activity(activity_type, None, {})

        # Test schema validation
        schema_test = instance.get_schema()

        return {
            "success": True,
            "activity_type": activity_type,
            "class_name": activity_class.__name__,
            "metadata": metadata,
            "schema_properties": list(schema.get("properties", {}).keys()),
            "has_validate_config": hasattr(instance, "validate_config"),
            "has_process_response": hasattr(instance, "process_response"),
            "has_calculate_results": hasattr(instance, "calculate_results"),
        }

    except Exception as e:
        return {
            "success": False,
            "activity_type": activity_type,
            "error": str(e),
        }
