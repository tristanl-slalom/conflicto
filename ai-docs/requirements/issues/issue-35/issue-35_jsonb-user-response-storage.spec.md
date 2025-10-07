# Technical Specification: Implement JSONB User Response Storage for Activity Framework

**GitHub Issue:** [#35](https://github.com/tristanl-slalom/conflicto/issues/35)
**Generated:** 2025-10-07T16:30:00Z

## Problem Statement

The current activity framework lacks flexible data storage for user responses, requiring backend schema changes for each new activity type. This creates development bottlenecks and tight coupling between activity implementations and database structure.

The solution involves implementing a flexible JSON-based storage system using PostgreSQL's JSONB capabilities to enable activity autonomy over data structures while maintaining query performance.

## Technical Requirements

### Database Schema Requirements

#### Enhanced User Responses Table
```sql
CREATE TABLE user_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    participant_id UUID NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    response_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Optimization indexes
CREATE INDEX idx_user_responses_session_activity ON user_responses(session_id, activity_id);
CREATE INDEX idx_user_responses_created_at ON user_responses(created_at);
CREATE INDEX idx_user_responses_participant ON user_responses(participant_id);
-- GIN index for JSONB queries
CREATE INDEX idx_user_responses_data_gin ON user_responses USING GIN(response_data);
```

#### Enhanced Activities Table
```sql
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    order_index INTEGER NOT NULL,
    status activity_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Optimization indexes
CREATE INDEX idx_activities_session_order ON activities(session_id, order_index);
CREATE INDEX idx_activities_status ON activities(status);
CREATE INDEX idx_activities_type ON activities(type);
-- GIN index for JSONB config queries
CREATE INDEX idx_activities_config_gin ON activities USING GIN(config);
```

### Data Model Requirements

#### JSONB Response Data Structure
```json
{
  "type": "activity_type_identifier",
  "version": "1.0",
  "data": {
    // Activity-specific response structure
    // Examples:
    // Planning Poker: {"estimate": 5, "confidence": "high"}
    // Poll: {"choice": "option_a", "timestamp": "2025-10-07T16:30:00Z"}
    // Word Cloud: {"words": ["innovation", "collaboration"]}
  },
  "metadata": {
    "client_timestamp": "2025-10-07T16:30:00Z",
    "device_type": "mobile",
    "user_agent": "Mozilla/5.0..."
  }
}
```

#### JSONB Activity Configuration Structure
```json
{
  "version": "1.0",
  "settings": {
    // Activity-specific configuration
    // Examples:
    // Planning Poker: {"cards": [1,2,3,5,8], "timer": 300}
    // Poll: {"options": ["A", "B", "C"], "multiple_choice": false}
    // Word Cloud: {"max_words": 50, "min_length": 3}
  },
  "display": {
    "title": "Activity Title",
    "description": "Activity Description",
    "instructions": "How to participate"
  },
  "constraints": {
    "time_limit": 300,
    "max_responses": 1,
    "allow_changes": true
  }
}
```

## API Specifications

### User Response Endpoints

#### Create Response
```http
POST /api/v1/sessions/{session_id}/activities/{activity_id}/responses
Content-Type: application/json

{
  "response_data": {
    "type": "planning_poker",
    "version": "1.0",
    "data": {
      "estimate": 5,
      "confidence": "high"
    }
  }
}

Response: 201 Created
{
  "id": "uuid",
  "session_id": "uuid",
  "activity_id": "uuid", 
  "participant_id": "uuid",
  "response_data": {...},
  "created_at": "2025-10-07T16:30:00Z"
}
```

#### Get Activity Responses (Aggregated)
```http
GET /api/v1/sessions/{session_id}/activities/{activity_id}/responses

Response: 200 OK
{
  "responses": [
    {
      "id": "uuid",
      "participant_id": "uuid",
      "response_data": {...},
      "created_at": "2025-10-07T16:30:00Z"
    }
  ],
  "summary": {
    "total_responses": 15,
    "unique_participants": 12,
    "last_updated": "2025-10-07T16:30:00Z"
  }
}
```

### Activity Configuration Endpoints

#### Create Activity
```http
POST /api/v1/sessions/{session_id}/activities
Content-Type: application/json

{
  "type": "planning_poker",
  "config": {
    "version": "1.0",
    "settings": {
      "cards": [1,2,3,5,8,13],
      "timer": 300
    },
    "display": {
      "title": "Sprint Planning - User Stories",
      "description": "Estimate story points for user stories"
    }
  },
  "order_index": 1
}
```

## Data Models

### SQLAlchemy Model Updates

#### UserResponse Model
```python
class UserResponse(Base):
    __tablename__ = "user_responses"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    activity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("activities.id", ondelete="CASCADE"))
    participant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"))
    response_data: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="user_responses")
    activity: Mapped["Activity"] = relationship("Activity", back_populates="user_responses")
    participant: Mapped["Participant"] = relationship("Participant", back_populates="responses")
```

#### Activity Model
```python
class Activity(Base):
    __tablename__ = "activities"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
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

## Interface Requirements

### JSON Schema Validation
- Implement JSON schema validation at application layer
- Version-aware schema validation for backward compatibility
- Graceful handling of schema validation errors

### Query Optimization Patterns
- Use JSONB operators for efficient querying: `->`, `->>`, `@>`, `?`
- Implement aggregation queries for activity results
- Optimize for real-time polling patterns (2-3 second intervals)

## Integration Points

### Activity Framework Integration
- Activity plugins must define response data schema
- Activity types register their expected JSON structure
- Backward compatibility for existing activity implementations

### Real-time Polling Integration
- Efficient querying for activity state changes
- Optimized response aggregation for viewer displays
- Minimal payload for participant polling

### Migration Integration
- Safe migration of existing data structures
- Rollback strategy for migration failures
- Data validation post-migration

## Acceptance Criteria

### Database Schema
- [ ] Migration successfully creates user_responses table with JSONB columns
- [ ] Migration successfully adds config JSONB column to activities table
- [ ] All required indexes are created for optimal query performance
- [ ] Foreign key constraints and cascade rules are properly implemented

### SQLAlchemy Models
- [ ] UserResponse model supports JSONB operations and relationships
- [ ] Activity model supports JSONB config field and relationships
- [ ] All model relationships are bidirectional and properly mapped
- [ ] JSON serialization/deserialization works correctly

### API Functionality
- [ ] Create response endpoint accepts and stores JSONB data
- [ ] Get responses endpoint returns properly formatted JSON responses
- [ ] Activity creation supports JSONB configuration storage
- [ ] Error handling for invalid JSON structure is implemented

### Performance
- [ ] Query performance meets <100ms requirements for typical loads
- [ ] Indexes optimize session/activity-based queries
- [ ] JSONB operations perform efficiently with sample data
- [ ] Real-time polling queries execute within performance targets

### Testing
- [ ] Unit tests cover JSONB storage and retrieval operations
- [ ] Integration tests validate end-to-end JSON response workflows
- [ ] Performance tests verify query optimization effectiveness
- [ ] Migration tests ensure data integrity and rollback capability

## Assumptions & Constraints

### Technical Assumptions
- PostgreSQL version 12+ for full JSONB support
- Application-layer JSON schema validation preferred over database constraints
- Activity types are known at development time for schema validation

### Performance Constraints
- Response data size limited to 1MB per response
- Activity configuration size limited to 10MB
- Query performance targets: <100ms for typical operations

### Compatibility Constraints
- Must maintain backward compatibility with existing session/participant models
- Migration must not break existing application functionality
- New schema must support existing test data structures

### Security Constraints
- JSONB data must be sanitized to prevent injection attacks
- Response data may contain sensitive information requiring proper access controls
- Activity configuration should not expose internal system details