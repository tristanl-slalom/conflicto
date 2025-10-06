"""
Session management API routes.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas import (
    SessionCreate, SessionUpdate, SessionResponse, SessionDetail, 
    SessionList, ErrorResponse
)
from app.services.session_service import SessionService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post(
    "/",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}}
)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    """
    Create a new session.
    
    Creates a new live event session with generated QR and admin codes.
    The session starts in DRAFT status.
    """
    try:
        session = await SessionService.create_session(db, session_data)
        stats = await SessionService.get_session_stats(db, session.id)
        
        return SessionResponse(
            id=session.id,
            title=session.title,
            description=session.description,
            status=session.status,
            qr_code=session.qr_code,
            admin_code=session.admin_code,
            max_participants=session.max_participants,
            created_at=session.created_at,
            updated_at=session.updated_at,
            started_at=session.started_at,
            completed_at=session.completed_at,
            participant_count=stats.get("participant_count", 0),
            activity_count=stats.get("activity_count", 0)
        )
    except Exception as e:
        logger.error("Failed to create session", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create session"
        )


@router.get(
    "/",
    response_model=SessionList,
    responses={400: {"model": ErrorResponse}}
)
async def list_sessions(
    offset: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> SessionList:
    """
    List all sessions with pagination.
    
    Returns a paginated list of all sessions, ordered by creation date (newest first).
    """
    try:
        sessions = await SessionService.list_sessions(db, offset, limit)
        session_responses = []
        
        for session in sessions:
            stats = await SessionService.get_session_stats(db, session.id)
            session_responses.append(
                SessionResponse(
                    id=session.id,
                    title=session.title,
                    description=session.description,
                    status=session.status,
                    qr_code=session.qr_code,
                    admin_code=session.admin_code,
                    max_participants=session.max_participants,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    started_at=session.started_at,
                    completed_at=session.completed_at,
                    participant_count=stats.get("participant_count", 0),
                    activity_count=stats.get("activity_count", 0)
                )
            )
        
        return SessionList(
            sessions=session_responses,
            total=len(session_responses),
            offset=offset,
            limit=limit
        )
    except Exception as e:
        logger.error("Failed to list sessions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve sessions"
        )


@router.get(
    "/{session_id}",
    response_model=SessionDetail,
    responses={404: {"model": ErrorResponse}}
)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
) -> SessionDetail:
    """
    Get detailed session information.
    
    Returns complete session details including activities and participants.
    """
    session = await SessionService.get_session(db, session_id, include_relations=True)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Convert activities and participants to response models
    from app.models.schemas import ActivityResponse, ParticipantResponse
    
    activities = [
        ActivityResponse(
            id=activity.id,
            session_id=activity.session_id,
            title=activity.title,
            description=activity.description,
            activity_type=activity.activity_type,
            configuration=activity.configuration,
            is_active=activity.is_active,
            order_index=activity.order_index,
            created_at=activity.created_at,
            updated_at=activity.updated_at,
            started_at=activity.started_at,
            completed_at=activity.completed_at
        )
        for activity in session.activities
    ]
    
    participants = [
        ParticipantResponse(
            id=participant.id,
            session_id=participant.session_id,
            display_name=participant.display_name,
            role=participant.role,
            is_active=participant.is_active,
            joined_at=participant.joined_at,
            last_seen_at=participant.last_seen_at,
            created_at=participant.joined_at,  # Use joined_at as created_at
            updated_at=participant.last_seen_at  # Use last_seen_at as updated_at
        )
        for participant in session.participants
    ]
    
    return SessionDetail(
        id=session.id,
        title=session.title,
        description=session.description,
        status=session.status,
        qr_code=session.qr_code,
        admin_code=session.admin_code,
        max_participants=session.max_participants,
        created_at=session.created_at,
        updated_at=session.updated_at,
        started_at=session.started_at,
        completed_at=session.completed_at,
        participant_count=len(participants),
        activity_count=len(activities),
        activities=activities,
        participants=participants
    )


@router.put(
    "/{session_id}",
    response_model=SessionResponse,
    responses={404: {"model": ErrorResponse}}
)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    """
    Update an existing session.
    
    Updates session details. Status transitions are tracked with timestamps.
    """
    session = await SessionService.update_session(db, session_id, session_data)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    stats = await SessionService.get_session_stats(db, session.id)
    
    return SessionResponse(
        id=session.id,
        title=session.title,
        description=session.description,
        status=session.status,
        qr_code=session.qr_code,
        admin_code=session.admin_code,
        max_participants=session.max_participants,
        created_at=session.created_at,
        updated_at=session.updated_at,
        started_at=session.started_at,
        completed_at=session.completed_at,
        participant_count=stats.get("participant_count", 0),
        activity_count=stats.get("activity_count", 0)
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}}
)
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a session.
    
    Permanently deletes a session and all associated data (activities, participants, responses).
    """
    success = await SessionService.delete_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@router.get(
    "/code/{code}",
    response_model=SessionResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_session_by_code(
    code: str,
    code_type: str = "qr",
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    """
    Get session by QR code or admin code.
    
    Allows participants to join via QR code or admins to access via admin code.
    """
    if code_type not in ["qr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code type. Must be 'qr' or 'admin'"
        )
    
    session = await SessionService.get_session_by_code(db, code, code_type)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    stats = await SessionService.get_session_stats(db, session.id)
    
    return SessionResponse(
        id=session.id,
        title=session.title,
        description=session.description,
        status=session.status,
        qr_code=session.qr_code if code_type == "admin" else None,  # Only show QR code to admins
        admin_code=session.admin_code if code_type == "admin" else None,  # Only show admin code to admins
        max_participants=session.max_participants,
        created_at=session.created_at,
        updated_at=session.updated_at,
        started_at=session.started_at,
        completed_at=session.completed_at,
        participant_count=stats.get("participant_count", 0),
        activity_count=stats.get("activity_count", 0)
    )