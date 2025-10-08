# Implementation Plan: Create Generic Activity-Agnostic CRUD API Endpoints

**GitHub Issue:** [#36](https://github.com/tristanl-slalom/conflicto/issues/36)
**Generated:** 2025-10-07T19:01:08Z

## Implementation Strategy

**UPDATED BASED ON CURRENT CODEBASE ANALYSIS:**

This implementation focuses on **adding missing real-time polling functionality** to the existing activity-agnostic architecture. The current codebase already has:

✅ **Already Implemented (No Changes Needed):**
- Activity and UserResponse models with JSONB support
- Activity CRUD endpoints in `/backend/app/routes/activities.py`
- User Response endpoints in `/backend/app/routes/user_responses.py`
- ActivityService and UserResponseService with business logic
- Pydantic schemas supporting JSONB operations

❌ **Missing Functionality to Implement:**
1. Session status polling endpoint for real-time updates
2. Activity-specific status polling endpoint
3. Incremental response updates using timestamp filtering
4. Enhanced service methods for efficient polling operations
5. New Pydantic schemas for status responses

The strategy prioritizes minimal changes to existing code while adding the missing real-time polling capabilities required for the activity framework.

## File Structure Changes

**UPDATED - Minimal Changes Based on Existing Code:**

### Files to Modify (Existing Files)

```
backend/app/
├── routes/
│   ├── sessions.py                  # Add session status polling endpoint
│   └── user_responses.py           # Add incremental updates endpoint
├── services/
│   ├── activity_service.py         # Add activity status polling method
│   ├── session_service.py          # Add session status polling method
│   └── user_response_service.py    # Add incremental updates method
├── models/
│   └── schemas.py                  # Add status response schemas
└── tests/
    ├── test_sessions_status.py     # New: session status polling tests
    ├── test_activities_status.py   # New: activity status polling tests
    └── test_user_responses_incremental.py # New: incremental updates tests
```

### New Files to Create (Minimal)

```
backend/app/tests/
├── test_status_polling.py          # Integration tests for all polling endpoints
└── test_incremental_updates.py     # Performance tests for incremental updates
```

### Files Already Existing (No Changes Needed)

```
✅ backend/app/db/models.py                    # Activity & UserResponse models complete
✅ backend/app/routes/activities.py           # All Activity CRUD operations exist
✅ backend/app/routes/user_responses.py       # Basic response operations exist
✅ backend/app/services/activity_service.py   # Core activity business logic exists
✅ backend/app/services/user_response_service.py # Core response business logic exists
✅ backend/app/models/jsonb_schemas/activity.py # Activity schemas complete
✅ backend/app/models/jsonb_schemas/user_response.py # Response schemas complete
```

## Implementation Steps

**UPDATED - Focused on Missing Functionality Only:**

### Step 1: Add Status Response Schemas
**Files Modified:** `backend/app/models/schemas.py`

1. Add SessionStatusResponse schema for session polling
2. Add ActivityStatusResponse schema for activity polling  
3. Add IncrementalResponseList schema for timestamp-based updates

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
```

### Step 2: Add Session Status Endpoint
**Files Modified:** `backend/app/routes/sessions.py`

1. Add `GET /sessions/{session_id}/status` endpoint
2. Integrate with existing SessionService for data retrieval
3. Add proper error handling and validation
4. Optimize for high-frequency polling

### Step 3: Enhance Activity Service for Status Polling
**Files Modified:** `backend/app/services/activity_service.py`

1. Add `get_activity_status()` method for efficient status retrieval
2. Optimize database queries for response counting
3. Add caching layer for frequently accessed activity status

### Step 4: Add Activity Status Polling Endpoint  
**Files Modified:** `backend/app/routes/activities.py`

1. Add `GET /sessions/{session_id}/activities/{activity_id}/status` endpoint
2. Integrate with enhanced ActivityService status methods
3. Add session-scoped validation

### Step 5: Enhance User Response Service for Incremental Updates
**Files Modified:** `backend/app/services/user_response_service.py`

1. Add `get_responses_since()` method with timestamp filtering
2. Optimize database queries using timestamp indexes
3. Add efficient pagination for large result sets

### Step 6: Add Incremental Updates Endpoint
**Files Modified:** `backend/app/routes/user_responses.py`

1. Add `GET /sessions/{session_id}/activities/{activity_id}/responses/since/{timestamp}` endpoint
2. Integrate with enhanced UserResponseService
3. Add proper timestamp validation and parsing

### Step 7: Comprehensive Testing
**Files Created:** Multiple test files for new functionality

1. **Unit Tests:**
   - Status endpoint response validation
   - Service method functionality
   - Timestamp filtering accuracy

2. **Integration Tests:**
   - Full polling endpoint workflows
   - High-frequency polling performance
   - Concurrent access testing

3. **Performance Tests:**
   - 50+ concurrent participant simulation
   - Polling frequency optimization
   - Database query performance validation

## Testing Strategy

### Unit Tests (80% Coverage Target)

#### Activity Service Tests
```python
# test_activity_service.py
- test_create_activity_success()
- test_create_activity_invalid_session()
- test_get_activity_success()
- test_get_activity_not_found()
- test_update_activity_success()
- test_delete_activity_success()
- test_list_activities_pagination()
- test_activity_ordering()
```

#### User Response Service Tests
```python
# test_user_response_service.py
- test_create_response_success()
- test_create_response_invalid_participant()
- test_list_responses_pagination()
- test_get_responses_since_timestamp()
- test_response_count_accuracy()
```

### Integration Tests

#### API Endpoint Tests
```python
# test_activities.py
- test_activity_crud_lifecycle()
- test_activity_session_validation()
- test_activity_json_flexibility()
- test_activity_status_polling()
- test_concurrent_activity_access()
```

#### Real-time Polling Tests
```python
# test_polling_performance.py
- test_session_status_performance()
- test_activity_status_performance()
- test_incremental_updates_accuracy()
- test_high_frequency_polling()
```

### Load Testing

#### Performance Requirements
- 50+ concurrent participants per session
- Response time < 200ms for CRUD operations
- Efficient handling of high-frequency polling
- Database connection pool optimization

#### Test Scenarios
```python
# Load test scenarios
- simulate_50_concurrent_participants()
- test_rapid_response_creation()
- test_continuous_polling_load()
- test_large_json_payload_handling()
```

## Deployment Considerations

### Database Migration
```bash
# Run migration to add JSONB columns
cd backend
alembic upgrade head
```

### Environment Variables
```bash
# Add to .env if needed
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
REDIS_CACHE_TTL=300
```

### Configuration Changes
```python
# Update database configuration for JSONB performance
- Enable JSONB gin indexes
- Configure connection pooling
- Set appropriate timeout values
```

### Monitoring Setup
```python
# Add monitoring for new endpoints
- Activity CRUD operation metrics
- Response creation rate monitoring
- Polling frequency monitoring
- Database query performance tracking
```

## Risk Assessment

### Technical Risks

#### JSONB Performance Risk
- **Risk:** Large JSON objects may impact query performance
- **Mitigation:** Implement JSON size limits, add monitoring, optimize indexes
- **Impact:** Medium

#### Polling Overhead Risk
- **Risk:** High-frequency polling may overwhelm server
- **Mitigation:** Implement rate limiting, connection pooling, caching
- **Impact:** High

#### Database Connection Exhaustion
- **Risk:** Concurrent users may exhaust connection pool
- **Mitigation:** Optimize pool size, implement connection monitoring
- **Impact:** High

### Business Risks

#### Activity Type Validation Risk
- **Risk:** Lack of activity type validation may allow invalid configurations
- **Mitigation:** Implement optional type registration, frontend validation
- **Impact:** Low

#### Data Migration Risk
- **Risk:** Existing data may not migrate cleanly to JSONB
- **Mitigation:** Comprehensive migration testing, rollback plan
- **Impact:** Medium

### Security Risks

#### JSON Injection Risk
- **Risk:** Malformed JSON in responses could cause issues
- **Mitigation:** Strict JSON validation, size limits, sanitization
- **Impact:** Medium

#### Rate Limiting Risk
- **Risk:** Polling endpoints vulnerable to DoS attacks
- **Mitigation:** Implement rate limiting, authentication validation
- **Impact:** Medium

## Estimated Effort

### Development Time Breakdown

#### Database & Models (1 day)
- Model enhancements: 2 hours
- Migration creation: 2 hours
- Testing and validation: 4 hours

#### Service Layer (2 days)
- Activity service implementation: 6 hours
- User response service enhancement: 4 hours
- Business logic testing: 6 hours

#### API Layer (2 days)
- Activity routes implementation: 6 hours
- User response routes enhancement: 4 hours
- Error handling and validation: 6 hours

#### Testing (2 days)
- Unit test implementation: 8 hours
- Integration test implementation: 6 hours
- Performance testing: 2 hours

#### Documentation & Integration (1 day)
- API documentation: 3 hours
- Code review and refinements: 3 hours
- Deployment preparation: 2 hours

### Total Estimated Effort: 3 days

**UPDATED EFFORT ESTIMATION:**

#### New Status Schemas (0.5 day)
- Status response schemas: 2 hours
- Schema integration and testing: 2 hours

#### Session Status Endpoint (0.5 day)
- Session status endpoint implementation: 2 hours
- Integration with existing SessionService: 2 hours

#### Activity Status Polling (1 day)
- Activity status service methods: 4 hours
- Activity status endpoint: 2 hours
- Testing and optimization: 2 hours

#### Incremental Updates (1 day)
- Timestamp-based filtering service method: 4 hours
- Incremental updates endpoint: 2 hours
- Performance optimization and testing: 2 hours

### Complexity Assessment: **Medium**
- Building on existing architecture reduces complexity significantly
- Real-time polling optimization requires careful attention
- Database query optimization for timestamp filtering needs focus
- Integration testing important for polling performance

### Dependencies
- No blocking dependencies (all required infrastructure exists)
- Coordination with frontend team for polling integration
- Performance testing environment for load validation

## Success Metrics

### Functional Metrics
- All 15 acceptance criteria passing
- 100% endpoint implementation complete
- Activity-agnostic behavior verified with 5+ different JSON structures
- Real-time polling working with <3 second update frequency

### Performance Metrics
- Average response time <200ms for CRUD operations
- Support for 50+ concurrent participants demonstrated
- Database query performance optimized (JSONB operations <100ms)
- Memory usage stable under load

### Quality Metrics
- Unit test coverage >80%
- Integration test coverage for all endpoints
- Zero critical security vulnerabilities
- API documentation complete and accurate