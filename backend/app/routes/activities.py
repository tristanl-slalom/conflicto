"""API routes for Activity operations."""

from datetime import datetime
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
from app.models.schemas import (
    ActivityStatusResponse,
    ActivityTypesListResponse,
    ActivityTypeSchemaResponse,
    FrameworkActivityCreate,
    ActivityTransitionRequest,
    ActivityValidationRequest,
    ActivityValidationResponse,
    ActivityResponseSubmissionRequest,
    ActivityResultsResponse,
    FrameworkActivityStatusResponse,
)
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


# ===== Framework-Enhanced Routes (specific paths must come before parameterized ones) =====


@router.get("/activities/types", response_model=ActivityTypesListResponse)
async def get_activity_types():
    """Get all available activity types from the framework."""
    try:
        activity_types = await ActivityService.get_activity_types()
        return ActivityTypesListResponse(activity_types=activity_types)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity types: {str(e)}",
        )


@router.get(
    "/activities/types/{activity_type}/schema",
    response_model=ActivityTypeSchemaResponse,
)
async def get_activity_type_schema(activity_type: str):
    """Get JSON schema for a specific activity type."""
    try:
        schema = await ActivityService.get_activity_type_schema(activity_type)
        return ActivityTypeSchemaResponse(activity_type=activity_type, schema=schema)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity schema: {str(e)}",
        )


@router.post("/activities/validate", response_model=ActivityValidationResponse)
async def validate_activity_configuration(
    validation_request: ActivityValidationRequest,
):
    """Validate activity configuration against type schema."""
    try:
        result = await ActivityService.validate_activity_config(
            activity_type=validation_request.activity_type,
            configuration=validation_request.configuration,
        )
        return ActivityValidationResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate activity configuration: {str(e)}",
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


# ===== Additional Framework Routes =====


@router.post(
    "/sessions/{session_id}/activities/framework",
    response_model=Activity,
    status_code=status.HTTP_201_CREATED,
)
async def create_framework_activity(
    session_id: int,
    activity_data: FrameworkActivityCreate,
    db: AsyncSession = Depends(get_db),
) -> Activity:
    """Create a new activity using the framework."""
    try:
        activity = await ActivityService.create_framework_activity(
            db=db,
            session_id=session_id,
            activity_type=activity_data.activity_type,
            title=activity_data.title,
            description=activity_data.description,
            configuration=activity_data.configuration,
            activity_metadata=activity_data.activity_metadata,
            order_index=activity_data.order_index,
        )
        return activity
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create framework activity: {str(e)}",
        )


@router.post("/activities/{activity_id}/transition", response_model=Activity)
async def transition_activity_state(
    activity_id: UUID,
    transition_request: ActivityTransitionRequest,
    db: AsyncSession = Depends(get_db),
) -> Activity:
    """Transition activity state using the framework state machine."""
    try:
        activity = await ActivityService.transition_activity_state(
            db=db,
            activity_id=activity_id,
            target_state=transition_request.target_state,
            reason=transition_request.reason,
            force=transition_request.force,
        )
        return activity
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transition activity state: {str(e)}",
        )


@router.post("/activities/{activity_id}/responses")
async def submit_activity_response(
    activity_id: UUID,
    participant_id: int,
    response_request: ActivityResponseSubmissionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit a participant response using the framework."""
    try:
        processed_response = await ActivityService.process_activity_response(
            db=db,
            activity_id=activity_id,
            participant_id=participant_id,
            response_data=response_request.response_data,
        )
        return {
            "success": True,
            "processed_response": processed_response,
            "message": "Response processed successfully",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process activity response: {str(e)}",
        )


@router.get("/activities/{activity_id}/results", response_model=ActivityResultsResponse)
async def get_activity_results(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ActivityResultsResponse:
    """Get calculated results for an activity."""
    try:
        results = await ActivityService.get_activity_results(
            db=db,
            activity_id=activity_id,
        )
        return ActivityResultsResponse(results=results, last_updated=datetime.utcnow())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity results: {str(e)}",
        )


@router.get(
    "/activities/{activity_id}/status/framework",
    response_model=FrameworkActivityStatusResponse,
)
async def get_framework_activity_status(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> FrameworkActivityStatusResponse:
    """Get enhanced activity status with framework information."""
    try:
        status_data = await ActivityService.get_framework_activity_status(
            db=db,
            activity_id=activity_id,
        )
        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )
        return FrameworkActivityStatusResponse(**status_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get framework activity status: {str(e)}",
        )
