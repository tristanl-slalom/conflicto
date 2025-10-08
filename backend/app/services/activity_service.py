"""Service layer for Activity operations with framework integration."""

import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Activity as DBActivity, UserResponse
from app.db.enums import ActivityStatus, ActivityState
from app.models.jsonb_schemas.activity import Activity, ActivityCreate, ActivityUpdate
from app.services.activity_framework import ActivityRegistry, ActivityStateMachine

logger = logging.getLogger(__name__)


class ActivityService:
    """Service class for Activity operations with framework integration."""

    @staticmethod
    async def create_activity(
        db: AsyncSession,
        session_id: int,
        activity_data: ActivityCreate,
    ) -> Activity:
        """Create a new activity."""
        # First validate that the session exists
        from app.services.session_service import SessionService

        session = await SessionService.get_session(db, session_id)
        if not session:
            raise ValueError(f"Session with id {session_id} not found")

        db_activity = DBActivity(
            session_id=session_id,
            type=activity_data.type,
            config=activity_data.config,
            order_index=activity_data.order_index,
            status=activity_data.status,
        )
        db.add(db_activity)
        await db.commit()
        await db.refresh(db_activity)

        # Convert DB model to JSONB schema model
        return Activity.model_validate(db_activity)

    @staticmethod
    async def get_activity(
        db: AsyncSession,
        activity_id: UUID,
    ) -> Activity | None:
        """Get a specific activity by ID."""
        query = select(DBActivity).where(DBActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()
        return Activity.model_validate(db_activity) if db_activity else None

    @staticmethod
    async def get_session_activities(
        db: AsyncSession,
        session_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Activity]:
        """Get all activities for a session."""
        query = (
            select(DBActivity)
            .where(DBActivity.session_id == session_id)
            .order_by(DBActivity.order_index)
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        db_activities = list(result.scalars().all())
        return [Activity.model_validate(db_activity) for db_activity in db_activities]

    @staticmethod
    async def get_session_activities_with_count(
        db: AsyncSession,
        session_id: int,
        offset: int = 0,
        limit: int = 100,
        status: Optional[ActivityStatus] = None,
    ) -> tuple[list[Activity], int]:
        """Get all activities for a session with total count."""
        # Build base query conditions
        conditions = [DBActivity.session_id == session_id]
        if status:
            conditions.append(DBActivity.status == status)

        # Get total count
        count_query = select(func.count(DBActivity.id)).where(*conditions)
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()

        # Get activities
        query = (
            select(DBActivity)
            .where(*conditions)
            .order_by(DBActivity.order_index)
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        db_activities = list(result.scalars().all())
        activities = [
            Activity.model_validate(db_activity) for db_activity in db_activities
        ]

        return activities, total_count

    @staticmethod
    async def update_activity(
        db: AsyncSession,
        activity_id: UUID,
        activity_data: ActivityUpdate,
    ) -> Activity | None:
        """Update an existing activity."""
        query = select(DBActivity).where(DBActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()

        if not db_activity:
            return None

        # Update fields that are provided
        if activity_data.type is not None:
            db_activity.type = activity_data.type
        if activity_data.config is not None:
            db_activity.config = activity_data.config
        if activity_data.order_index is not None:
            db_activity.order_index = activity_data.order_index
        if activity_data.status is not None:
            db_activity.status = activity_data.status

        await db.commit()
        await db.refresh(db_activity)
        return Activity.model_validate(db_activity)

    @staticmethod
    async def delete_activity(
        db: AsyncSession,
        activity_id: UUID,
    ) -> bool:
        """Delete an activity."""
        query = select(DBActivity).where(DBActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()

        if not db_activity:
            return False

        await db.delete(db_activity)
        await db.commit()
        return True

    @staticmethod
    async def update_activity_status(
        db: AsyncSession,
        activity_id: UUID,
        status: ActivityStatus,
    ) -> Activity | None:
        """Update activity status."""
        query = select(DBActivity).where(DBActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()

        if not db_activity:
            return None

        db_activity.status = status
        await db.commit()
        await db.refresh(db_activity)
        return Activity.model_validate(db_activity)

    @staticmethod
    async def get_active_activity(
        db: AsyncSession,
        session_id: int,
    ) -> Activity | None:
        """Get the currently active activity for a session."""
        query = (
            select(DBActivity)
            .where(
                DBActivity.session_id == session_id,
                DBActivity.status == ActivityStatus.ACTIVE,
            )
            .order_by(desc(DBActivity.updated_at))
            .limit(1)
        )
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()
        return Activity.model_validate(db_activity) if db_activity else None

    @staticmethod
    async def get_activity_status(
        db: AsyncSession,
        session_id: int,
        activity_id: UUID,
    ) -> dict[str, Any]:
        """Get activity status information for polling."""
        # Get the activity
        activity = await ActivityService.get_activity(db, activity_id)
        if not activity or activity.session_id != session_id:
            return None

        # Count responses for this activity
        response_count_query = select(func.count(UserResponse.id)).where(
            UserResponse.activity_id == activity_id
        )
        response_count_result = await db.execute(response_count_query)
        response_count = response_count_result.scalar() or 0

        # Get last response time
        last_response_query = select(func.max(UserResponse.created_at)).where(
            UserResponse.activity_id == activity_id
        )
        last_response_result = await db.execute(last_response_query)
        last_response_at = last_response_result.scalar()

        return {
            "activity_id": activity_id,
            "status": activity.status,
            "response_count": response_count,
            "last_response_at": last_response_at,
            "last_updated": activity.updated_at,
        }

    # ===== Framework-Enhanced Methods =====

    @staticmethod
    async def create_framework_activity(
        db: AsyncSession,
        session_id: int,
        activity_type: str,
        title: str,
        description: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        activity_metadata: Optional[dict[str, Any]] = None,
        order_index: int = 0,
    ) -> Activity:
        """Create a new activity using the framework.

        Args:
            db: Database session
            session_id: ID of the session
            activity_type: Type of activity (must be registered)
            title: Activity title
            description: Optional description
            configuration: Activity-specific configuration
            activity_metadata: Framework metadata
            order_index: Order index for the activity

        Returns:
            Created Activity instance

        Raises:
            ValueError: If activity type is not registered or configuration is invalid
        """
        # Validate activity type is registered
        if not ActivityRegistry.is_registered(activity_type):
            raise ValueError(f"Unknown activity type: {activity_type}")

        # Get activity class and validate configuration
        configuration = configuration or {}
        activity_instance = ActivityRegistry.create_activity(
            activity_type, None, configuration
        )

        if not activity_instance.validate_config(configuration):
            raise ValueError("Invalid activity configuration")

        # First validate that the session exists
        from app.services.session_service import SessionService

        session = await SessionService.get_session(db, session_id)
        if not session:
            raise ValueError(f"Session with id {session_id} not found")

        # Merge default metadata with provided metadata
        default_metadata = activity_instance.get_default_metadata()
        final_metadata = {**default_metadata, **(activity_metadata or {})}

        # Create database record
        db_activity = DBActivity(
            session_id=session_id,
            type=activity_type,
            title=title,
            description=description,
            config=configuration,  # Keep for backwards compatibility
            configuration=configuration,  # New framework field
            activity_metadata=final_metadata,
            order_index=order_index,
            status=ActivityStatus.DRAFT,  # Keep for backwards compatibility
            state=ActivityState.DRAFT,  # New framework field
        )

        db.add(db_activity)
        await db.commit()
        await db.refresh(db_activity)

        logger.info(f"Created activity {db_activity.id} of type {activity_type}")
        return Activity.model_validate(db_activity)

    @staticmethod
    async def transition_activity_state(
        db: AsyncSession,
        activity_id: UUID,
        target_state: str,
        reason: Optional[str] = None,
        force: bool = False,
    ) -> Activity:
        """Transition activity state using state machine.

        Args:
            db: Database session
            activity_id: ID of the activity
            target_state: Target state to transition to
            reason: Optional reason for the transition
            force: If True, skip validation (use with caution)

        Returns:
            Updated Activity instance

        Raises:
            ValueError: If activity not found or transition is invalid
        """
        query = select(DBActivity).where(DBActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()

        if not db_activity:
            raise ValueError(f"Activity with id {activity_id} not found")

        # Use state machine to validate and perform transition
        if not ActivityStateMachine.transition(
            db_activity, target_state, reason, force
        ):
            valid_transitions = ActivityStateMachine.get_valid_transitions(
                db_activity.state
            )
            raise ValueError(
                f"Cannot transition from {db_activity.state} to {target_state}. "
                f"Valid transitions: {valid_transitions}"
            )

        # Also update the legacy status field for backwards compatibility
        if target_state == ActivityState.ACTIVE:
            db_activity.status = ActivityStatus.ACTIVE
        elif target_state == ActivityState.EXPIRED:
            db_activity.status = ActivityStatus.COMPLETED

        await db.commit()
        await db.refresh(db_activity)

        logger.info(f"Activity {activity_id} transitioned to {target_state}")
        return Activity.model_validate(db_activity)

    @staticmethod
    async def get_activity_types() -> list[dict[str, Any]]:
        """Get all available activity types.

        Returns:
            List of activity type metadata
        """
        return [
            {
                "id": activity_type,
                "name": metadata["name"],
                "description": metadata["description"],
                "version": metadata["version"],
            }
            for activity_type, metadata in ActivityRegistry.get_all_types().items()
        ]

    @staticmethod
    async def get_activity_type_schema(activity_type: str) -> dict[str, Any]:
        """Get JSON schema for activity type.

        Args:
            activity_type: Activity type identifier

        Returns:
            JSON schema for the activity configuration

        Raises:
            ValueError: If activity type is not registered
        """
        return ActivityRegistry.get_schema(activity_type)

    @staticmethod
    async def validate_activity_config(
        activity_type: str,
        configuration: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate activity configuration.

        Args:
            activity_type: Activity type identifier
            configuration: Configuration to validate

        Returns:
            Validation result with success status and errors
        """
        try:
            activity_instance = ActivityRegistry.create_activity(
                activity_type, None, configuration
            )
            is_valid = activity_instance.validate_config(configuration)

            return {
                "valid": is_valid,
                "errors": [] if is_valid else ["Configuration validation failed"],
            }
        except ValueError as e:
            return {
                "valid": False,
                "errors": [str(e)],
            }

    @staticmethod
    async def process_activity_response(
        db: AsyncSession,
        activity_id: UUID,
        participant_id: int,
        response_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Process a participant response using activity framework.

        Args:
            db: Database session
            activity_id: ID of the activity
            participant_id: ID of the participant
            response_data: Response data from participant

        Returns:
            Processed response data

        Raises:
            ValueError: If activity not found, not active, or response is invalid
        """
        # Get the activity
        query = select(DBActivity).where(DBActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()

        if not db_activity:
            raise ValueError(f"Activity with id {activity_id} not found")

        # Check if activity is active
        if db_activity.state != ActivityState.ACTIVE:
            raise ValueError(
                f"Activity is not active (current state: {db_activity.state})"
            )

        # Create activity instance and process response
        activity_instance = ActivityRegistry.create_activity(
            db_activity.type, activity_id, db_activity.configuration
        )

        try:
            processed_response = activity_instance.process_response(
                participant_id, response_data
            )
        except Exception as e:
            raise ValueError(f"Response processing failed: {str(e)}")

        # Store the response (use existing UserResponse storage)
        from app.services.user_response_service import UserResponseService

        await UserResponseService.create_user_response(
            db=db,
            session_id=db_activity.session_id,
            activity_id=activity_id,
            participant_id=participant_id,
            response_data=processed_response,
        )

        logger.info(
            f"Processed response for activity {activity_id} from participant {participant_id}"
        )
        return processed_response

    @staticmethod
    async def get_activity_results(
        db: AsyncSession,
        activity_id: UUID,
    ) -> dict[str, Any]:
        """Get calculated results for an activity.

        Args:
            db: Database session
            activity_id: ID of the activity

        Returns:
            Calculated activity results
        """
        # Get the activity
        query = select(DBActivity).where(DBActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()

        if not db_activity:
            raise ValueError(f"Activity with id {activity_id} not found")

        # Get all responses for this activity
        responses_query = select(UserResponse).where(
            UserResponse.activity_id == activity_id
        )
        responses_result = await db.execute(responses_query)
        responses = responses_result.scalars().all()

        # Create activity instance and calculate results
        activity_instance = ActivityRegistry.create_activity(
            db_activity.type, activity_id, db_activity.configuration
        )

        response_data = [
            {"response_data": r.response_data, "created_at": r.created_at}
            for r in responses
        ]
        results = activity_instance.calculate_results(response_data)

        return results

    @staticmethod
    async def check_and_expire_activities(db: AsyncSession) -> list[UUID]:
        """Check for activities that should be automatically expired.

        This method should be called periodically (e.g., via background task)
        to automatically expire activities that have reached their expiration time.

        Args:
            db: Database session

        Returns:
            List of activity IDs that were expired
        """
        # Get all active activities with expiration times
        query = select(DBActivity).where(
            DBActivity.state == ActivityState.ACTIVE,
            DBActivity.expires_at.isnot(None),
        )
        result = await db.execute(query)
        activities = result.scalars().all()

        expired_activities = ActivityStateMachine.check_expired_activities(activities)

        if expired_activities:
            await db.commit()
            logger.info(f"Auto-expired {len(expired_activities)} activities")

        return [activity.id for activity in expired_activities]

    @staticmethod
    async def get_framework_activity_status(
        db: AsyncSession,
        activity_id: UUID,
    ) -> dict[str, Any]:
        """Get enhanced activity status information for framework.

        Args:
            db: Database session
            activity_id: ID of the activity

        Returns:
            Enhanced activity status information
        """
        # Get basic status using existing method
        basic_status = await ActivityService.get_activity_status(
            db,
            None,
            activity_id,  # session_id not needed for this query
        )

        if not basic_status:
            return None

        # Get the activity for enhanced information
        query = select(DBActivity).where(DBActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()

        if not db_activity:
            return None

        # Add framework-specific status information
        enhanced_status = {
            **basic_status,
            "state": db_activity.state,
            "expires_at": db_activity.expires_at,
            "activity_metadata": db_activity.activity_metadata,
            "valid_transitions": ActivityStateMachine.get_valid_transitions(
                db_activity.state
            ),
        }

        # Add calculated results if available
        try:
            results = await ActivityService.get_activity_results(db, activity_id)
            enhanced_status["results"] = results
        except Exception as e:
            logger.warning(
                f"Could not calculate results for activity {activity_id}: {e}"
            )

        return enhanced_status
