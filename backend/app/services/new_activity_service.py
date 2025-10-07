"""Service layer for New Activity operations."""
from typing import List
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NewActivity, ActivityStatus
from app.models.jsonb_schemas.new_activity import NewActivityCreate, NewActivityUpdate


class NewActivityService:
    """Service class for New Activity operations."""
    
    @staticmethod
    async def create_activity(
        db: AsyncSession,
        session_id: int,
        activity_data: NewActivityCreate,
    ) -> NewActivity:
        """Create a new activity."""
        db_activity = NewActivity(
            session_id=session_id,
            type=activity_data.type,
            config=activity_data.config,
            order_index=activity_data.order_index,
        )
        db.add(db_activity)
        await db.commit()
        await db.refresh(db_activity)
        return db_activity

    @staticmethod
    async def get_activity(
        db: AsyncSession,
        activity_id: UUID,
    ) -> NewActivity | None:
        """Get an activity by ID."""
        query = select(NewActivity).where(NewActivity.id == activity_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_session_activities(
        db: AsyncSession,
        session_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> List[NewActivity]:
        """Get all activities for a session ordered by order_index."""
        query = (
            select(NewActivity)
            .where(NewActivity.session_id == session_id)
            .order_by(NewActivity.order_index)
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_activity(
        db: AsyncSession,
        activity_id: UUID,
        activity_data: NewActivityUpdate,
    ) -> NewActivity | None:
        """Update an existing activity."""
        query = select(NewActivity).where(NewActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()
        
        if db_activity:
            update_data = activity_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_activity, field, value)
            
            await db.commit()
            await db.refresh(db_activity)
        
        return db_activity

    @staticmethod
    async def delete_activity(
        db: AsyncSession,
        activity_id: UUID,
    ) -> bool:
        """Delete an activity."""
        query = select(NewActivity).where(NewActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()
        
        if db_activity:
            await db.delete(db_activity)
            await db.commit()
            return True
        
        return False

    @staticmethod
    async def update_activity_status(
        db: AsyncSession,
        activity_id: UUID,
        status: ActivityStatus,
    ) -> NewActivity | None:
        """Update activity status."""
        query = select(NewActivity).where(NewActivity.id == activity_id)
        result = await db.execute(query)
        db_activity = result.scalar_one_or_none()
        
        if db_activity:
            db_activity.status = status
            await db.commit()
            await db.refresh(db_activity)
        
        return db_activity

    @staticmethod
    async def get_active_activity(
        db: AsyncSession,
        session_id: int,
    ) -> NewActivity | None:
        """Get the currently active activity for a session."""
        query = select(NewActivity).where(
            NewActivity.session_id == session_id,
            NewActivity.status == ActivityStatus.ACTIVE,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def reorder_activities(
        db: AsyncSession,
        session_id: int,
        activity_orders: List[tuple[UUID, int]],
    ) -> bool:
        """Reorder activities by updating their order_index."""
        try:
            for activity_id, new_order in activity_orders:
                query = select(NewActivity).where(
                    NewActivity.id == activity_id,
                    NewActivity.session_id == session_id,
                )
                result = await db.execute(query)
                activity = result.scalar_one_or_none()
                
                if activity:
                    activity.order_index = new_order
            
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False