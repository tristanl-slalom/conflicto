"""API routes for User Response operations."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas.user_response import (
    UserResponse,
    UserResponseCreate,
    UserResponseUpdate,
    UserResponseList,
    UserResponseSummary,
)
from app.services.user_response_service import UserResponseService

router = APIRouter(prefix="/api/v1", tags=["user-responses"])


@router.post(
    "/sessions/{session_id}/activities/{activity_id}/responses",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_response(
    session_id: int,
    activity_id: UUID,
    participant_id: int,  # TODO: Extract from auth context in production
    response_data: UserResponseCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new user response for an activity."""
    try:
        response = await UserResponseService.create_response(
            db=db,
            session_id=session_id,
            activity_id=activity_id,
            participant_id=participant_id,
            response_data=response_data,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create response: {str(e)}",
        )


@router.get(
    "/sessions/{session_id}/activities/{activity_id}/responses",
    response_model=UserResponseList
)
async def get_activity_responses(
    session_id: int,
    activity_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> UserResponseList:
    """Get all responses for a specific activity with summary."""
    try:
        responses = await UserResponseService.get_activity_responses(
            db=db,
            session_id=session_id,
            activity_id=activity_id,
            offset=offset,
            limit=limit,
        )
        summary_data = await UserResponseService.get_response_summary(
            db=db,
            session_id=session_id,
            activity_id=activity_id,
        )
        summary = UserResponseSummary(**summary_data)
        
        return UserResponseList(responses=responses, summary=summary)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get responses: {str(e)}",
        )


@router.get(
    "/sessions/{session_id}/activities/{activity_id}/responses/{participant_id}",
    response_model=UserResponse | None
)
async def get_participant_response(
    session_id: int,
    activity_id: UUID,
    participant_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserResponse | None:
    """Get a specific participant's response for an activity."""
    try:
        response = await UserResponseService.get_participant_response(
            db=db,
            session_id=session_id,
            activity_id=activity_id,
            participant_id=participant_id,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get participant response: {str(e)}",
        )


@router.put(
    "/responses/{response_id}",
    response_model=UserResponse
)
async def update_response(
    response_id: UUID,
    response_data: UserResponseUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update an existing user response."""
    try:
        response = await UserResponseService.update_response(
            db=db,
            response_id=response_id,
            response_data=response_data,
        )
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found",
            )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update response: {str(e)}",
        )


@router.delete(
    "/responses/{response_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_response(
    response_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a user response."""
    try:
        deleted = await UserResponseService.delete_response(
            db=db,
            response_id=response_id,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete response: {str(e)}",
        )


@router.get(
    "/sessions/{session_id}/participants/{participant_id}/responses",
    response_model=List[UserResponse]
)
async def get_participant_responses(
    session_id: int,
    participant_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> List[UserResponse]:
    """Get all responses by a specific participant in a session."""
    try:
        responses = await UserResponseService.get_responses_by_participant(
            db=db,
            session_id=session_id,
            participant_id=participant_id,
            offset=offset,
            limit=limit,
        )
        return responses
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get participant responses: {str(e)}",
        )