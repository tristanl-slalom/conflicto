# Technical Specification: Create Generic Activity-Agnostic CRUD API Endpoints

**GitHub Issue:** [#36](https://github.com/tristanl-slalom/conflicto/issues/36)
**Generated:** 2025-10-07T19:01:08Z

## Problem Statement

**UPDATED BASED ON CURRENT CODEBASE ANALYSIS:**

The Caja platform already has most activity-agnostic CRUD functionality implemented, including:
- ✅ Activity and UserResponse models with JSONB support
- ✅ Basic Activity CRUD operations in `/app/routes/activities.py`
- ✅ User Response creation and retrieval in `/app/routes/user_responses.py`
- ✅ ActivityService and UserResponseService implementations
- ✅ Pydantic schemas with JSONB support

**What's MISSING for Issue #36:**
- Real-time polling endpoints for session and activity status
- Incremental updates endpoint for responses since timestamp
- Session-scoped activity status endpoints
- Enhanced pagination and performance optimizations for polling

## Technical Requirements

**UPDATED - Focus on Missing Functionality:**

### Real-time Polling Requirements
- Session status polling endpoint with current activity and participant count
- Activity-specific status polling with response counts and timestamps  
- Incremental response updates using timestamp-based filtering
- Optimized database queries for high-frequency polling (2-3 second intervals)

### Performance Requirements (Already Partially Met)
- Existing CRUD operations already support JSONB and async patterns
- Need to add caching layer for polling endpoints
- Optimize for 50+ concurrent participants per session
- Add efficient pagination for incremental updates

### Missing API Endpoints Only
- `GET /api/sessions/{session_id}/status` - Session polling
- `GET /api/sessions/{session_id}/activities/{activity_id}/status` - Activity polling  
- `GET /api/sessions/{session_id}/activities/{activity_id}/responses/since/{timestamp}` - Incremental updates

## API Specifications

**UPDATED - Only Missing Endpoints Listed:**

### ✅ Already Implemented (No Changes Needed)
- Activity CRUD: `POST/GET/PUT/DELETE /api/v1/sessions/{session_id}/activities`
- User Responses: `POST/GET /api/v1/sessions/{session_id}/activities/{activity_id}/responses`
- Activity Status Updates: `PATCH /api/v1/activities/{activity_id}/status`

### ❌ Missing Endpoints to Implement

#### Session Status Polling
```http
GET /api/sessions/{session_id}/status

Response: 200 OK
{
  "session_id": 123,
  "status": "active",
  "current_activity_id": "uuid",
  "participant_count": 25,
  "last_updated": "2025-10-07T19:00:00Z"
}
```

#### Activity Status Polling  
```http
GET /api/sessions/{session_id}/activities/{activity_id}/status

Response: 200 OK
{
  "activity_id": "uuid",
  "status": "active", 
  "response_count": 15,
  "last_response_at": "2025-10-07T19:00:30Z",
  "last_updated": "2025-10-07T19:00:00Z"
}
```

#### Incremental Response Updates
```http
GET /api/sessions/{session_id}/activities/{activity_id}/responses/since/{timestamp}

Response: 200 OK
{
  "items": [
    {
      "id": "uuid",
      "participant_id": 123,
      "activity_id": "uuid", 
      "response_data": {},
      "created_at": "2025-10-07T19:00:30Z",
      "updated_at": "2025-10-07T19:00:30Z"
    }
  ],
  "since": "2025-10-07T19:00:00Z",
  "count": 1
}
```

## Data Models

**UPDATED - Existing Models Analysis:**

### ✅ Already Implemented (No Changes Needed)
Current models in `/backend/app/db/models.py` already support the requirements:

```python
class Activity(Base):
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"))
    type: Mapped[str] = mapped_column(String(50))  # Activity-agnostic type
    config: Mapped[dict] = mapped_column(JSONB, default=dict)  # JSONB for any structure
    order_index: Mapped[int] = mapped_column(Integer)
    status: Mapped[ActivityStatus] = mapped_column(String(20), default=ActivityStatus.DRAFT)
    # ... timestamps and relationships already present

class UserResponse(Base):
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"))
    activity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("activities.id"))
    participant_id: Mapped[int] = mapped_column(Integer, ForeignKey("participants.id"))
    response_data: Mapped[dict] = mapped_column(JSONB)  # JSONB for any structure
    # ... timestamps and relationships already present
```

### ❌ New Schemas Needed Only for Status Endpoints

```python
class SessionStatusResponse(BaseModel):
    session_id: int
    status: SessionStatus
    current_activity_id: Optional[UUID] = None
    participant_count: int
    last_updated: datetime

class ActivityStatusResponse(BaseModel):
    activity_id: UUID
    status: ActivityStatus
    response_count: int
    last_response_at: Optional[datetime] = None
    last_updated: datetime

class IncrementalResponseList(BaseModel):
    items: List[UserResponse]
    since: datetime
    count: int
```

## Interface Requirements

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid activity configuration",
    "details": {
      "field": "config.question",
      "reason": "Required field missing"
    }
  }
}
```

### Pagination Response Format
```json
{
  "items": [],
  "total": 100,
  "limit": 20,
  "offset": 0,
  "has_next": true,
  "has_prev": false
}
```

## Integration Points

### Database Integration
- PostgreSQL with JSONB columns for flexible data storage
- SQLAlchemy ORM with async support
- Alembic migrations for schema changes
- Database connection pooling via asyncpg

### Session Integration
- Validate session existence before activity operations
- Enforce session-activity relationship integrity
- Handle session state transitions (draft → active → completed)
- Session-scoped participant validation

### Authentication Integration
- JWT token validation for all endpoints
- Role-based access control (admin, participant)
- Session membership validation for participants

### Caching Integration
- Redis caching for frequently accessed session data
- Activity configuration caching
- Response count caching for real-time updates

## Acceptance Criteria

**UPDATED - Focused on Missing Functionality:**

### Functional Requirements
- [ ] Session status polling endpoint returns current activity and participant count
- [ ] Activity status polling endpoint returns response count and timestamps
- [ ] Incremental updates endpoint returns responses since given timestamp
- [ ] All polling endpoints perform efficiently under high-frequency requests (2-3 second intervals)
- [ ] Existing CRUD operations continue to work with any JSON structure (already verified)
- [ ] Real-time polling endpoints integrate with existing session/activity management

### Performance Requirements
- [ ] New polling endpoints complete within 200ms under normal load
- [ ] System continues to support 50+ concurrent participants with new endpoints
- [ ] Incremental updates efficiently filter by timestamp using database indexes
- [ ] Polling endpoints handle high-frequency requests without overwhelming server

### Quality Requirements
- [ ] Comprehensive error handling for new endpoints with clear messages
- [ ] New endpoint documentation auto-generated and accurate
- [ ] Unit test coverage >80% for new polling functionality
- [ ] Integration tests cover polling endpoint behavior under load

## Assumptions & Constraints

### Technical Assumptions
- PostgreSQL JSONB provides sufficient performance for JSON operations
- 2-3 second polling intervals meet real-time requirements
- Session and participant entities already exist in database
- JWT authentication system already implemented

### Business Constraints
- No WebSocket implementation required (polling-based MVP)
- Activity type registration optional for MVP
- Frontend handles activity-specific validation
- Backward compatibility with existing session/participant APIs

### Performance Constraints
- Database connection pool limited by server resources
- JSONB query performance depends on JSON structure complexity
- Polling frequency limited by server capacity
- Response payload size impacts network performance

### Security Constraints
- All endpoints require authentication
- Participants can only access their own session data
- Activity configurations may contain sensitive data
- Rate limiting required for polling endpoints