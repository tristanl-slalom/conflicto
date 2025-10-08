"""
Participant routes for QR code onboarding and session management.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.database import get_db
from app.services.participant_service import ParticipantService
from app.models.schemas import (
    ParticipantJoinRequest,
    ParticipantJoinResponse,
    ParticipantHeartbeatRequest,
    ParticipantHeartbeatResponse,
    ParticipantListResponse,
    NicknameValidationResponse,
    ErrorResponse,
)

logger = get_logger(__name__)
router = APIRouter(tags=["participants"])


def get_participant_service(db: Session = Depends(get_db)) -> ParticipantService:
    """Dependency to get participant service."""
    return ParticipantService(db)


@router.post(
    "/sessions/{session_id}/join",
    response_model=ParticipantJoinResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def join_session(
    session_id: int,
    join_request: ParticipantJoinRequest,
    service: ParticipantService = Depends(get_participant_service),
):
    """
    Join a session with a nickname via QR code scan.

    - **session_id**: Session ID from QR code URL
    - **nickname**: Desired participant nickname (1-50 characters)

    Returns participant_id and current session state for synchronization.
    """
    try:
        response = await service.join_session(session_id, join_request)
        logger.info(
            "Participant joined session",
            session_id=session_id,
            participant_id=response.participant_id,
            nickname=join_request.nickname,
        )
        return response

    except ValueError as e:
        logger.warning(
            "Failed to join session",
            session_id=session_id,
            nickname=join_request.nickname,
            error=str(e),
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/sessions/{session_id}/nicknames/validate",
    response_model=NicknameValidationResponse,
)
async def validate_nickname(
    session_id: int,
    nickname: str = Query(..., min_length=1, max_length=50),
    service: ParticipantService = Depends(get_participant_service),
):
    """
    Validate if a nickname is available in a session.

    - **session_id**: Session ID to check nickname availability
    - **nickname**: Nickname to validate

    Returns availability status and suggested alternatives if taken.
    """
    try:
        response = await service.validate_nickname(session_id, nickname)
        return response

    except Exception as e:
        logger.error(
            "Failed to validate nickname",
            session_id=session_id,
            nickname=nickname,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/participants/{participant_id}/heartbeat",
    response_model=ParticipantHeartbeatResponse,
    responses={404: {"model": ErrorResponse}},
)
async def update_heartbeat(
    participant_id: UUID,
    heartbeat_request: ParticipantHeartbeatRequest,
    service: ParticipantService = Depends(get_participant_service),
):
    """
    Update participant heartbeat and get current activity context.

    - **participant_id**: UUID of participant
    - **activity_context**: Optional context data from current activity

    Returns computed status and current activity information.
    Should be called every 15-30 seconds by participant clients.
    """
    try:
        response = await service.update_heartbeat(participant_id, heartbeat_request)
        return response

    except ValueError as e:
        logger.warning(
            "Failed to update heartbeat",
            participant_id=str(participant_id),
            error=str(e),
        )
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/sessions/{session_id}/participants",
    response_model=ParticipantListResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_session_participants(
    session_id: int,
    service: ParticipantService = Depends(get_participant_service),
):
    """
    Get all participants in a session with their computed status.

    - **session_id**: Session ID to get participants for

    Returns list of participants with online/idle/disconnected status
    computed from their last heartbeat timing.
    """
    try:
        participants = await service.get_session_participants(session_id)
        return ParticipantListResponse(
            participants=participants, total_count=len(participants)
        )

    except Exception as e:
        logger.error(
            "Failed to get session participants",
            session_id=session_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/participants/{participant_id}",
    responses={
        204: {"description": "Participant removed successfully"},
        404: {"model": ErrorResponse},
    },
)
async def remove_participant(
    participant_id: UUID,
    service: ParticipantService = Depends(get_participant_service),
):
    """
    Remove a participant from their session.

    - **participant_id**: UUID of participant to remove

    Admin operation to kick participants or clean up disconnected users.
    """
    try:
        success = await service.remove_participant(participant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Participant not found")

        logger.info("Participant removed", participant_id=str(participant_id))
        return {"message": "Participant removed successfully"}

    except Exception as e:
        logger.error(
            "Failed to remove participant",
            participant_id=str(participant_id),
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Internal server error")
