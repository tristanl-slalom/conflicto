"""API routes for New Activity operations."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import ActivityStatus
from app.models.schemas.new_activity import (
    NewActivity,
    NewActivityCreate,
    NewActivityUpdate,
    NewActivityList,
)
from app.services.new_activity_service import NewActivityService

router = APIRouter(prefix="/api/v1", tags=["new-activities"])


@router.post(
    "/sessions/{session_id}/activities",
    response_model=NewActivity,
    status_code=status.HTTP_201_CREATED
)
async def create_activity(
    session_id: int,
    activity_data: NewActivityCreate,
    db: AsyncSession = Depends(get_db),
) -> NewActivity:
    """Create a new activity for a session."""
    try:
        activity = await NewActivityService.create_activity(
            db=db,
            session_id=session_id,
            activity_data=activity_data,
        )
        return activity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create activity: {str(e)}",
        )


@router.get(
    "/sessions/{session_id}/activities",
    response_model=NewActivityList
)
async def get_session_activities(
    session_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> NewActivityList:
    """Get all activities for a session."""
    try:
        activities = await NewActivityService.get_session_activities(
            db=db,
            session_id=session_id,
            offset=offset,
            limit=limit,
        )
        return NewActivityList(activities=activities, total_count=len(activities))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get activities: {str(e)}",
        )


@router.get(
    "/activities/{activity_id}",
    response_model=NewActivity
)
async def get_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> NewActivity:
    """Get an activity by ID."""
    try:
        activity = await NewActivityService.get_activity(
            db=db,
            activity_id=activity_id,
        )
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )
        return activity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get activity: {str(e)}",
        )


@router.put(
    "/activities/{activity_id}",
    response_model=NewActivity
)
async def update_activity(
    activity_id: UUID,
    activity_data: NewActivityUpdate,
    db: AsyncSession = Depends(get_db),
) -> NewActivity:
    """Update an existing activity."""
    try:
        activity = await NewActivityService.update_activity(
            db=db,
            activity_id=activity_id,
            activity_data=activity_data,
        )
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )
        return activity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update activity: {str(e)}",
        )


@router.delete(
    "/activities/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an activity."""
    try:
        deleted = await NewActivityService.delete_activity(
            db=db,
            activity_id=activity_id,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete activity: {str(e)}",
        )


@router.patch(
    "/activities/{activity_id}/status",
    response_model=NewActivity
)
async def update_activity_status(
    activity_id: UUID,
    status: ActivityStatus,
    db: AsyncSession = Depends(get_db),
) -> NewActivity:
    """Update activity status."""
    try:
        activity = await NewActivityService.update_activity_status(
            db=db,
            activity_id=activity_id,
            status=status,
        )
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )
        return activity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update activity status: {str(e)}",
        )


@router.get(
    "/sessions/{session_id}/activities/active",
    response_model=NewActivity | None
)
async def get_active_activity(
    session_id: int,
    db: AsyncSession = Depends(get_db),
) -> NewActivity | None:
    """Get the currently active activity for a session."""
    try:
        activity = await NewActivityService.get_active_activity(
            db=db,
            session_id=session_id,
        )
        return activity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get active activity: {str(e)}",
        )