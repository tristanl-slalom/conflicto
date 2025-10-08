"""Service layer for Activity operations."""

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Activity as DBActivity, UserResponse
from app.db.enums import ActivityStatus
from app.models.jsonb_schemas.activity import Activity, ActivityCreate, ActivityUpdate


class ActivityService:
    """Service class for Activity operations."""

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
