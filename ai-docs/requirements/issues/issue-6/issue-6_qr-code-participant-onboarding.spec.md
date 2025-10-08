# Technical Specification: Implement QR Code Generation and Participant Onboarding

**GitHub Issue:** [#6](https://github.com/tristanl-slalom/conflicto/issues/6)  
**Generated:** 2025-10-07T21:00:00Z  

## Problem Statement

Participants currently lack an easy way to join interactive sessions without complex account creation or setup processes. The platform needs to provide seamless mobile onboarding through QR code scanning that allows participants to join sessions at any time, even after activities have started, while maintaining unique identity and connection status tracking.

## Technical Requirements

### QR Code Generation
- Frontend-based QR code generation using session ID directly
- QR codes generated client-side for immediate display without server requests
- QR code content contains join URL with session ID: `https://app.caja.dbash.dev/join/{session_id}`
- QR codes must be persistent and displayed throughout all session activities
- QR codes should be optimized for scanning from various distances and screen sizes
- No server-side QR generation or join tokens required

### Participant Onboarding Flow
- Mobile-optimized joining interface accessible via QR code scan
- Nickname selection with real-time uniqueness validation
- Session state synchronization for late joiners to receive current activity state
- Connection recovery mechanism for participants with network interruptions
- Support for participants joining mid-session without disrupting ongoing activities

### Real-time Participant Management
- Automatic participant connection status tracking based on heartbeat timing
- Status calculation: online (<30s), idle (30s-2min), disconnected (>2min)
- Participant list management with nickname collision detection and resolution
- Graceful handling of duplicate nicknames with automatic suffix generation
- Participant session context persistence across connection drops

## API Specifications

### Backend Endpoints

#### Session Access (No QR endpoint needed)
QR codes generated client-side using session ID directly from session data.
Join URL format: `https://app.caja.dbash.dev/join/{session_id}`

#### Participant Join
```
POST /api/sessions/{session_id}/join
Request: {
  "nickname": "string"
}
Response: {
  "participant_id": "uuid",
  "session_state": {
    "current_activity": "activity_type",
    "activity_data": {...},
    "participants": [...]
  }
}
```

#### Participant Heartbeat
```
POST /api/participants/{participant_id}/heartbeat
Request: {}
Response: {
  "acknowledged": true,
  "last_seen": "2025-10-07T21:00:00Z",
  "participant_context": {
    "current_activity": "activity_type",
    "activity_data": {...},
    "participant_state": {...},
    "session_participants": [...]
  }
}
```
Note: Status is automatically determined by backend based on time since last heartbeat. Heartbeat returns current activity context for synchronization.

#### Nickname Validation
```
GET /api/sessions/{session_id}/nicknames/validate?nickname={nickname}
Response: {
  "available": boolean,
  "suggested_alternatives": ["nickname1", "nickname2"]
}
```

## Data Models

### Database Schema Updates

#### Sessions Table Enhancement
```sql
ALTER TABLE sessions ADD COLUMN allow_late_join BOOLEAN DEFAULT true;
```
Note: No QR token fields needed since QR codes are generated client-side using session ID.

#### Participants Table
```sql
CREATE TABLE participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    nickname VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'online',
    joined_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    connection_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(session_id, nickname)
);

CREATE INDEX idx_participants_session_status ON participants(session_id, status);
CREATE INDEX idx_participants_last_seen ON participants(last_seen);
```

### Pydantic Models

#### ParticipantJoinRequest
```python
class ParticipantJoinRequest(BaseModel):
    nickname: str = Field(min_length=1, max_length=50)
```
Note: No QRCodeResponse model needed since QR codes are generated client-side.

#### ParticipantResponse
```python
class ParticipantResponse(BaseModel):
    participant_id: UUID
    nickname: str
    status: str  # Computed based on last_seen: "online"|"idle"|"disconnected"
    joined_at: datetime
    last_seen: datetime

class ParticipantHeartbeatResponse(BaseModel):
    acknowledged: bool
    last_seen: datetime
    participant_context: dict  # Current activity context for synchronization
```

## Interface Requirements

### Viewer Interface (Large Screen)
- Persistent QR code display in corner/sidebar throughout all activities
- QR code should not obstruct activity content
- Include text instructions: "Scan to join session"
- Display current participant count and recent joiners
- QR code remains static (session ID never changes)

### Participant Interface (Mobile-Optimized)
- Landing page optimized for mobile scanning experience
- Large, clear nickname input field with validation feedback
- "Join Session" button with loading states
- Error handling for invalid tokens, full sessions, or network issues
- Automatic redirect to current activity after successful join
- Connection status indicator and reconnection handling

### Admin Interface
- Toggle for allowing/disallowing late joiners
- Participant management panel with kick/ban functionality
- Participant connection status monitoring

## Integration Points

### QR Code Library
- Integration with JavaScript QR code library (e.g., `https://qr-code-styling.com/`)
- No server-side dependencies required

### Session Management Integration
- QR codes tied to static session ID (never changes)
- QR codes remain valid as long as session is accessible
- No need for QR code regeneration since session ID is immutable
- Integration with existing session polling mechanism

### Activity Framework Integration
- Late joiners receive current activity state upon connection
- Activity-specific participant limits and validation

### Real-time Synchronization
- Participant heartbeat via polling-based synchronization (15-30 second intervals)
- Backend computes status automatically based on heartbeat timing
- Status thresholds: online (<30s), idle (30s-2min), disconnected (>2min)
- Heartbeat returns current activity context for participant synchronization
- Optimistic UI updates with conflict resolution
- Graceful degradation for network interruptions

## Acceptance Criteria

- [ ] Generate dynamic QR codes for active sessions
- [ ] Display persistent small QR code throughout all session activities  
- [ ] Create mobile-optimized joining interface
- [ ] Implement nickname validation and uniqueness checking
- [ ] Track participant connection status in real-time
- [ ] Handle late joiners gracefully with current activity state sync
- [ ] Support connection recovery for dropped participants

## Assumptions & Constraints

### Technical Assumptions
- Participants will primarily use mobile devices for scanning and interaction
- QR codes will be scanned from screens (not printed materials)
- Session URLs have reasonable length limits for QR code encoding
- Polling-based synchronization sufficient for real-time participant management
- SQLite/PostgreSQL JSONB support available for flexible participant data storage

### Business Constraints
- MVP focuses on basic QR joining without advanced security features
- No user accounts required - nickname-based identity sufficient
- Maximum 50 participants per session for performance considerations
- QR codes remain valid for session duration (no automatic expiry)

### Security Considerations
- Session ID provides basic session access control
- No sensitive data transmitted in QR codes (only session ID)
- Rate limiting on join attempts to prevent abuse
- Participant nickname filtering for inappropriate content
- Public session access via session ID (no additional authentication for MVP)

### Performance Constraints
- Join flow should complete within 2 seconds on mobile networks
- Participant status updates should not impact main session performance
- UI should remain responsive during participant join/leave events