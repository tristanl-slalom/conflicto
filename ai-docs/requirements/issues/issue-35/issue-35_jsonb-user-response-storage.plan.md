# Implementation Plan: Implement JSONB User Response Storage for Activity Framework

**GitHub Issue:** [#35](https://github.com/tristanl-slalom/conflicto/issues/35)
**Generated:** 2025-10-07T16:30:00Z

## Implementation Strategy

This implementation follows a phased approach to minimize disruption and ensure data integrity:

1. **Phase 1**: Database schema updates with new tables and indexes
2. **Phase 2**: SQLAlchemy model updates and relationship mapping
3. **Phase 3**: API endpoint implementation for JSONB operations
4. **Phase 4**: Migration script creation and testing
5. **Phase 5**: Comprehensive testing and validation

The implementation prioritizes backward compatibility while introducing the flexible JSONB-based storage system for future activity development.

## File Structure Changes

### New Files to Create

```
backend/
├── migrations/versions/
│   └── {timestamp}_add_jsonb_user_response_storage.py
├── app/db/models/
│   ├── user_response.py (new)
│   └── activity.py (enhanced)
├── app/models/schemas/
│   ├── user_response.py (new)
│   └── activity.py (enhanced)
├── app/routes/
│   ├── user_responses.py (new)
│   └── activities.py (enhanced)
├── app/services/
│   ├── user_response_service.py (new)
│   └── activity_service.py (enhanced)
└── tests/
    ├── test_user_responses.py (new)
    ├── test_activities_jsonb.py (new)
    └── test_migration_jsonb.py (new)
```

### Existing Files to Modify

```
backend/
├── app/db/models.py (update imports and relationships)
├── app/models/schemas.py (update imports)
├── app/routes/__init__.py (register new routes)
├── app/main.py (register new routers)
└── pyproject.toml (if new dependencies needed)
```

## Implementation Steps

### Step 1: Database Migration Script
**File**: `backend/migrations/versions/{timestamp}_add_jsonb_user_response_storage.py`

```python
"""Add JSONB user response storage

Revision ID: {revision_id}
Revises: {previous_revision}
Create Date: 2025-10-07 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '{revision_id}'
down_revision = '{previous_revision}'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create activity_status enum if not exists
    activity_status = postgresql.ENUM('draft', 'active', 'completed', 'cancelled', name='activity_status')
    activity_status.create(op.get_bind(), checkfirst=True)
    
    # Create user_responses table
    op.create_table('user_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('activity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('response_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create activities table
    op.create_table('activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('status', activity_status, nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for optimal performance
    op.create_index('idx_user_responses_session_activity', 'user_responses', ['session_id', 'activity_id'])
    op.create_index('idx_user_responses_created_at', 'user_responses', ['created_at'])
    op.create_index('idx_user_responses_participant', 'user_responses', ['participant_id'])
    op.create_index('idx_user_responses_data_gin', 'user_responses', ['response_data'], postgresql_using='gin')
    
    op.create_index('idx_activities_session_order', 'activities', ['session_id', 'order_index'])
    op.create_index('idx_activities_status', 'activities', ['status'])
    op.create_index('idx_activities_type', 'activities', ['type'])
    op.create_index('idx_activities_config_gin', 'activities', ['config'], postgresql_using='gin')

def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_activities_config_gin', table_name='activities')
    op.drop_index('idx_activities_type', table_name='activities')
    op.drop_index('idx_activities_status', table_name='activities')
    op.drop_index('idx_activities_session_order', table_name='activities')
    
    op.drop_index('idx_user_responses_data_gin', table_name='user_responses')
    op.drop_index('idx_user_responses_participant', table_name='user_responses')
    op.drop_index('idx_user_responses_created_at', table_name='user_responses')
    op.drop_index('idx_user_responses_session_activity', table_name='user_responses')
    
    # Drop tables
    op.drop_table('activities')
    op.drop_table('user_responses')
    
    # Drop enum
    activity_status = postgresql.ENUM('draft', 'active', 'completed', 'cancelled', name='activity_status')
    activity_status.drop(op.get_bind(), checkfirst=True)
```

### Step 2: SQLAlchemy Model Implementation
**File**: `backend/app/db/models/user_response.py`

```python
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from .activity import Activity
    from .participant import Participant
    from .session import Session

class UserResponse(Base):
    __tablename__ = "user_responses"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    activity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("activities.id", ondelete="CASCADE"))
    participant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"))
    response_data: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="user_responses")
    activity: Mapped["Activity"] = relationship("Activity", back_populates="user_responses")
    participant: Mapped["Participant"] = relationship("Participant", back_populates="responses")
```

**File**: `backend/app/db/models/activity.py`

```python
import enum
from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from .session import Session
    from .user_response import UserResponse

class ActivityStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Activity(Base):
    __tablename__ = "activities"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(50))
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    order_index: Mapped[int] = mapped_column(Integer)
    status: Mapped[ActivityStatus] = mapped_column(Enum(ActivityStatus), default=ActivityStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="activities")
    user_responses: Mapped[List["UserResponse"]] = relationship("UserResponse", back_populates="activity", cascade="all, delete-orphan")
```

### Step 3: Pydantic Schema Implementation
**File**: `backend/app/models/schemas/user_response.py`

```python
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field

class UserResponseBase(BaseModel):
    response_data: Dict[str, Any] = Field(..., description="Activity-specific response data in JSON format")

class UserResponseCreate(UserResponseBase):
    pass

class UserResponseUpdate(UserResponseBase):
    pass

class UserResponse(UserResponseBase):
    id: UUID
    session_id: UUID
    activity_id: UUID
    participant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponseSummary(BaseModel):
    total_responses: int
    unique_participants: int
    last_updated: datetime

class UserResponseList(BaseModel):
    responses: List[UserResponse]
    summary: UserResponseSummary
```

### Step 4: Service Layer Implementation
**File**: `backend/app/services/user_response_service.py`

```python
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user_response import UserResponse
from app.models.schemas.user_response import UserResponseCreate, UserResponseUpdate

class UserResponseService:
    @staticmethod
    async def create_response(
        db: AsyncSession,
        session_id: UUID,
        activity_id: UUID,
        participant_id: UUID,
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
        session_id: UUID,
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
        return result.scalars().all()

    @staticmethod
    async def get_response_summary(
        db: AsyncSession,
        session_id: UUID,
        activity_id: UUID,
    ) -> dict:
        """Get summary statistics for activity responses."""
        total_query = select(func.count(UserResponse.id)).where(
            UserResponse.session_id == session_id,
            UserResponse.activity_id == activity_id,
        )
        unique_query = select(func.count(func.distinct(UserResponse.participant_id))).where(
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
```

### Step 5: API Route Implementation
**File**: `backend/app/routes/user_responses.py`

```python
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas.user_response import (
    UserResponse,
    UserResponseCreate,
    UserResponseList,
    UserResponseSummary,
)
from app.services.user_response_service import UserResponseService

router = APIRouter(prefix="/api/v1/sessions/{session_id}/activities/{activity_id}/responses", tags=["responses"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_response(
    session_id: UUID,
    activity_id: UUID,
    participant_id: UUID,  # TODO: Extract from auth context
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

@router.get("/", response_model=UserResponseList)
async def get_activity_responses(
    session_id: UUID,
    activity_id: UUID,
    offset: int = 0,
    limit: int = 100,
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
```

### Step 6: Testing Implementation
**File**: `backend/tests/test_user_responses.py`

```python
import pytest
from httpx import AsyncClient

from app.db.models.activity import Activity, ActivityStatus
from app.db.models.user_response import UserResponse

pytestmark = pytest.mark.asyncio

class TestUserResponses:
    async def test_create_user_response(self, async_client: AsyncClient, test_session, test_activity, test_participant):
        """Test creating a user response with JSONB data."""
        response_data = {
            "response_data": {
                "type": "planning_poker",
                "version": "1.0",
                "data": {
                    "estimate": 5,
                    "confidence": "high"
                },
                "metadata": {
                    "client_timestamp": "2025-10-07T16:30:00Z",
                    "device_type": "mobile"
                }
            }
        }
        
        response = await async_client.post(
            f"/api/v1/sessions/{test_session.id}/activities/{test_activity.id}/responses",
            json=response_data,
            params={"participant_id": str(test_participant.id)}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["response_data"]["type"] == "planning_poker"
        assert data["response_data"]["data"]["estimate"] == 5

    async def test_get_activity_responses(self, async_client: AsyncClient, test_session, test_activity):
        """Test retrieving activity responses with summary."""
        response = await async_client.get(
            f"/api/v1/sessions/{test_session.id}/activities/{test_activity.id}/responses"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "responses" in data
        assert "summary" in data
        assert "total_responses" in data["summary"]
        assert "unique_participants" in data["summary"]

    async def test_jsonb_query_performance(self, db_session, test_session, test_activity):
        """Test JSONB query performance with indexes."""
        # Create multiple responses for testing
        for i in range(100):
            response = UserResponse(
                session_id=test_session.id,
                activity_id=test_activity.id,
                participant_id=test_participant.id,
                response_data={
                    "type": "test",
                    "data": {"value": i}
                }
            )
            db_session.add(response)
        
        await db_session.commit()
        
        # Test JSONB query with index usage
        from sqlalchemy import text
        query = text("""
            SELECT * FROM user_responses 
            WHERE session_id = :session_id 
            AND activity_id = :activity_id 
            AND response_data @> '{"type": "test"}'
        """)
        
        result = await db_session.execute(
            query, 
            {"session_id": test_session.id, "activity_id": test_activity.id}
        )
        responses = result.fetchall()
        assert len(responses) == 100
```

## Testing Strategy

### Unit Tests
- **Model Tests**: Validate JSONB storage and retrieval in SQLAlchemy models
- **Service Tests**: Test business logic for user responses and activities
- **Schema Tests**: Validate Pydantic serialization/deserialization

### Integration Tests
- **API Tests**: End-to-end testing of JSONB response endpoints
- **Database Tests**: Validate JSONB queries and index usage
- **Migration Tests**: Ensure schema changes work correctly

### Performance Tests
- **Query Performance**: Validate <100ms response times with sample data
- **Index Usage**: Confirm GIN indexes optimize JSONB queries
- **Concurrent Access**: Test multiple users submitting responses simultaneously

## Deployment Considerations

### Migration Script Execution
1. Backup existing database before migration
2. Run migration in maintenance window for production
3. Validate data integrity post-migration
4. Monitor performance after index creation

### Environment Variables
No new environment variables required for this implementation.

### Database Configuration
- Ensure PostgreSQL version 12+ for full JSONB support
- Monitor disk usage growth with JSONB data
- Consider connection pool sizing for increased load

## Risk Assessment

### Potential Issues
1. **Migration Performance**: Large datasets may cause extended migration times
2. **Index Creation**: GIN indexes on JSONB may be slow to create
3. **Query Complexity**: Complex JSONB queries may impact performance
4. **Data Validation**: Invalid JSON structure could cause application errors

### Mitigation Strategies
1. **Staged Migration**: Migrate schema in off-peak hours with proper testing
2. **Index Monitoring**: Monitor index creation progress and database performance
3. **Query Optimization**: Use EXPLAIN ANALYZE to optimize JSONB queries
4. **Validation Layer**: Implement comprehensive JSON schema validation

### Rollback Plan
- Migration includes proper downgrade() method
- Database backup before migration execution
- Feature flags to disable JSONB functionality if issues arise

## Estimated Effort

### Development Time
- **Migration Script**: 4 hours
- **Model Implementation**: 6 hours
- **Service Layer**: 8 hours
- **API Routes**: 6 hours
- **Testing**: 12 hours
- **Documentation**: 4 hours

**Total Estimated Time**: 40 hours (1 week of development)

### Complexity Assessment
- **Low Risk**: Database schema changes (well-defined requirements)
- **Medium Risk**: JSONB query optimization (requires performance testing)
- **Low Risk**: API implementation (follows existing patterns)

### Dependencies
- Requires PostgreSQL with JSONB support
- Depends on existing session/participant models
- May require coordination with frontend team for JSON schema definitions