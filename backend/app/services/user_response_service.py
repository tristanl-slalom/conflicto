"""Service layer for User Response operations."""
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserResponse
from app.models.jsonb_schemas.user_response import (
    UserResponseCreate,
    UserResponseUpdate,
)


class UserResponseService:
    """Service class for User Response operations."""

    @staticmethod
    async def create_response(
        db: AsyncSession,
        session_id: int,
        activity_id: UUID,
        participant_id: int,
        response_data: UserResponseCreate,
    ) -> UserResponse:
        """Create a new user response."""
        db_response = UserResponse(
            session_id=session_id,
            activity_id=activity_id,
            participant_id=participant_id,
            response_data=response_data.response_data,
        )
        db.add(db_response)
        await db.commit()
        await db.refresh(db_response)
        return db_response

    @staticmethod
    async def get_activity_responses(
        db: AsyncSession,
        session_id: int,
        activity_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> List[UserResponse]:
        """Get all responses for a specific activity."""
        query = (
            select(UserResponse)
            .where(
                UserResponse.session_id == session_id,
                UserResponse.activity_id == activity_id,
            )
            .order_by(desc(UserResponse.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_participant_response(
        db: AsyncSession,
        session_id: int,
        activity_id: UUID,
        participant_id: int,
    ) -> UserResponse | None:
        """Get a specific participant's response for an activity."""
        query = select(UserResponse).where(
            UserResponse.session_id == session_id,
            UserResponse.activity_id == activity_id,
            UserResponse.participant_id == participant_id,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_response(
        db: AsyncSession,
        response_id: UUID,
        response_data: UserResponseUpdate,
    ) -> UserResponse | None:
        """Update an existing user response."""
        query = select(UserResponse).where(UserResponse.id == response_id)
        result = await db.execute(query)
        db_response = result.scalar_one_or_none()

        if db_response:
            db_response.response_data = response_data.response_data
            await db.commit()
            await db.refresh(db_response)

        return db_response

    @staticmethod
    async def delete_response(
        db: AsyncSession,
        response_id: UUID,
    ) -> bool:
        """Delete a user response."""
        query = select(UserResponse).where(UserResponse.id == response_id)
        result = await db.execute(query)
        db_response = result.scalar_one_or_none()

        if db_response:
            await db.delete(db_response)
            await db.commit()
            return True

        return False

    @staticmethod
    async def get_response_summary(
        db: AsyncSession,
        session_id: int,
        activity_id: UUID,
    ) -> dict:
        """Get summary statistics for activity responses."""
        total_query = select(func.count(UserResponse.id)).where(
            UserResponse.session_id == session_id,
            UserResponse.activity_id == activity_id,
        )
        unique_query = select(
            func.count(func.distinct(UserResponse.participant_id))
        ).where(
            UserResponse.session_id == session_id,
            UserResponse.activity_id == activity_id,
        )
        last_updated_query = select(func.max(UserResponse.updated_at)).where(
            UserResponse.session_id == session_id,
            UserResponse.activity_id == activity_id,
        )

        total_result = await db.execute(total_query)
        unique_result = await db.execute(unique_query)
        last_updated_result = await db.execute(last_updated_query)

        return {
            "total_responses": total_result.scalar() or 0,
            "unique_participants": unique_result.scalar() or 0,
            "last_updated": last_updated_result.scalar(),
        }

    @staticmethod
    async def get_responses_by_participant(
        db: AsyncSession,
        session_id: int,
        participant_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> List[UserResponse]:
        """Get all responses by a specific participant in a session."""
        query = (
            select(UserResponse)
            .where(
                UserResponse.session_id == session_id,
                UserResponse.participant_id == participant_id,
            )
            .order_by(desc(UserResponse.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_responses_since(
        db: AsyncSession,
        session_id: int,
        activity_id: UUID,
        since: datetime,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        """Get responses created since a specific timestamp for incremental updates."""
        query = (
            select(UserResponse)
            .where(
                UserResponse.session_id == session_id,
                UserResponse.activity_id == activity_id,
                UserResponse.created_at > since,
            )
            .order_by(UserResponse.created_at)
            .limit(limit)
        )
        result = await db.execute(query)
        responses = list(result.scalars().all())

        return {
            "items": responses,
            "since": since,
            "count": len(responses),
        }
