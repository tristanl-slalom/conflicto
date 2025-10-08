"""API routes for Activity operations."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.enums import ActivityStatus
from app.models.jsonb_schemas.activity import (
    Activity,
    ActivityCreate,
    ActivityList,
    ActivityUpdate,
)
from app.models.schemas import ActivityStatusResponse
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/api/v1", tags=["activities"])


@router.post(
    "/sessions/{session_id}/activities",
    response_model=Activity,
    status_code=status.HTTP_201_CREATED,
)
async def create_activity(
    session_id: int,
    activity_data: ActivityCreate,
    db: AsyncSession = Depends(get_db),
) -> Activity:
    """Create a new activity for a session."""
    try:
        activity = await ActivityService.create_activity(
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


@router.get("/sessions/{session_id}/activities", response_model=ActivityList)
async def get_session_activities(
    session_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ActivityStatus] = Query(
        None, description="Filter activities by status"
    ),
    db: AsyncSession = Depends(get_db),
) -> ActivityList:
    """Get all activities for a session."""
    try:
        (
            activities,
            total_count,
        ) = await ActivityService.get_session_activities_with_count(
            db=db,
            session_id=session_id,
            offset=offset,
            limit=limit,
            status=status,
        )
        return ActivityList(activities=activities, total=total_count)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get activities: {str(e)}",
        )


@router.get("/activities/{activity_id}", response_model=Activity)
async def get_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Activity:
    """Get an activity by ID."""
    try:
        activity = await ActivityService.get_activity(
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


@router.put("/activities/{activity_id}", response_model=Activity)
async def update_activity(
    activity_id: UUID,
    activity_data: ActivityUpdate,
    db: AsyncSession = Depends(get_db),
) -> Activity:
    """Update an existing activity."""
    try:
        activity = await ActivityService.update_activity(
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


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an activity."""
    try:
        deleted = await ActivityService.delete_activity(
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


@router.patch("/activities/{activity_id}/status", response_model=Activity)
async def update_activity_status(
    activity_id: UUID,
    status: ActivityStatus,
    db: AsyncSession = Depends(get_db),
) -> Activity:
    """Update activity status."""
    try:
        activity = await ActivityService.update_activity_status(
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


@router.get("/sessions/{session_id}/activities/active", response_model=Activity | None)
async def get_active_activity(
    session_id: int,
    db: AsyncSession = Depends(get_db),
) -> Activity | None:
    """Get the currently active activity for a session."""
    try:
        activity = await ActivityService.get_active_activity(
            db=db,
            session_id=session_id,
        )
        return activity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get active activity: {str(e)}",
        )


@router.get(
    "/sessions/{session_id}/activities/{activity_id}/status",
    response_model=ActivityStatusResponse,
)
async def get_activity_status(
    session_id: int,
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ActivityStatusResponse:
    """Get activity status for real-time polling."""
    try:
        status_data = await ActivityService.get_activity_status(
            db=db,
            session_id=session_id,
            activity_id=activity_id,
        )
        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )
        return ActivityStatusResponse(**status_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get activity status: {str(e)}",
        )
