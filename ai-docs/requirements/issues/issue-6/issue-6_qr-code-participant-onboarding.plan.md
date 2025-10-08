# Implementation Plan: Implement QR Code Generation and Participant Onboarding

**GitHub Issue:** [#6](https://github.com/tristanl-slalom/conflicto/issues/6)  
**Generated:** 2025-10-07T21:00:00Z  

## Implementation Strategy

This implementation follows a **frontend-first, client-side QR generation approach** that integrates seamlessly with the existing session management and polling-based synchronization architecture. The strategy prioritizes **participant experience** while maintaining **session integrity** and **real-time updates**.

### Core Approach
1. **Frontend QR Generation**: Generate QR codes client-side using session ID directly
2. **Backend Participant Management**: Focus on participant models, join validation, and API endpoints  
3. **Progressive Mobile Enhancement**: Build viewer QR display, then mobile joining interface
4. **Real-time Integration**: Leverage existing polling mechanism for participant status updates
5. **Graceful Degradation**: Ensure functionality works across network conditions and device capabilities

## File Structure Changes

### New Files to Create

#### Backend Files
```
backend/app/
├── models/
│   └── participants.py          # Participant SQLAlchemy models
├── routes/
│   └── participants.py          # Participant join/management endpoints
├── services/
│   └── participant_service.py   # Participant management logic
└── db/
    └── migrations/
        └── {timestamp}_add_participants_table.py

# Note: No backend QR code dependencies needed
```

#### Frontend Files
```
frontend/src/
├── components/
│   ├── qr-code/
│   │   ├── QRCodeDisplay.tsx        # Viewer QR code component
│   │   └── QRCodeContainer.tsx      # QR code with participant info
│   ├── participants/
│   │   ├── ParticipantJoinForm.tsx  # Mobile join form
│   │   ├── ParticipantList.tsx      # Admin participant management
│   │   └── ParticipantStatus.tsx    # Connection status indicator
│   └── layouts/
│       └── JoinLayout.tsx           # Mobile-optimized join page layout
├── routes/
│   └── join.tsx                     # Public join route (/join/$sessionId)
├── hooks/
│   ├── useParticipants.ts          # Participant management hook
│   ├── useQRCode.ts                # QR code generation hook
│   └── useParticipantJoin.ts       # Join flow hook
├── api/
│   └── participants.ts             # Participant API client functions
└── lib/
    ├── qr-generator.ts             # Client-side QR code generation utilities
    └── qr-scanner.ts               # QR code scanning utilities (if needed)

frontend/package.json               # Add qr-code-styling library
```

#### Test Files
```
backend/tests/
├── test_participants.py           # Participant management tests
└── test_participant_service.py    # Service layer tests

frontend/src/__tests__/
├── components/
│   ├── QRCodeDisplay.test.tsx
│   ├── ParticipantJoinForm.test.tsx
│   └── ParticipantList.test.tsx
└── hooks/
    ├── useParticipants.test.ts
    └── useParticipantJoin.test.ts
```

### Files to Modify

#### Backend Modifications
```
backend/app/
├── db/models.py                    # Add participant model imports
├── main.py                         # Register new route modules
└── core/settings.py               # Add QR code configuration

backend/app/models/schemas.py       # Add participant response schemas
```

#### Frontend Modifications
```
frontend/src/
├── routes/
│   ├── admin/sessions/$sessionId.tsx    # Add QR code display
│   └── viewer/sessions/$sessionId.tsx   # Add QR code display
├── router.tsx                          # Add public join routes
└── api/generated.ts                    # Will be updated by OpenAPI generation
```

## Implementation Steps

### Step 1: Backend Data Layer (Database & Models)
**Files**: `backend/app/db/migrations/`, `backend/app/models/participants.py`

1. Create Alembic migration for participants table
   - UUID primary key with session foreign key relationship
   - Nickname uniqueness constraint per session
   - Status tracking (online/offline/disconnected)
   - Timestamps for joined_at and last_seen
   - JSONB field for flexible connection metadata

2. Create SQLAlchemy Participant model
   - Proper relationships with Session model
   - Computed status property based on last_seen timestamp
   - Automatic timestamp updates on heartbeat
   - Nickname length and character validation

3. Update existing Session model
   - Add allow_late_join boolean flag
   - Create relationship with participants
   - Note: No QR token fields needed since QR codes are generated client-side

### Step 2: Backend Service Layer (Business Logic)
**Files**: `backend/app/services/participant_service.py`

1. **ParticipantService Implementation**
   - Nickname validation and collision detection
   - Participant join flow with state synchronization
   - Automatic status computation based on heartbeat timing
   - Heartbeat processing with activity context retrieval
   - Current activity state packaging for participant synchronization
   - Late joiner activity state synchronization
   - Graceful participant removal and cleanup

### Step 3: Backend API Layer (Endpoints)
**Files**: `backend/app/routes/participants.py`

1. **Participant Endpoints**
   - `POST /api/sessions/{session_id}/join` - Join session with nickname (no token required)
   - `GET /api/sessions/{session_id}/nicknames/validate` - Validate nickname availability
   - `POST /api/participants/{participant_id}/heartbeat` - Maintain heartbeat + return activity context
   - `GET /api/sessions/{session_id}/participants` - List session participants (with computed status)
   - `DELETE /api/participants/{participant_id}` - Remove participant (admin)

2. **Request/Response Schema Updates**
   - Add participant models to OpenAPI schema
   - Update session response to include participant counts

### Step 4: Frontend QR Code Generation & Display (Viewer Interface)
**Files**: `frontend/src/components/qr-code/`, `frontend/src/lib/qr-generator.ts`, viewer route modifications

1. **QR Code Generation Library Setup**
   - Install client-side QR code library (`https://qr-code-styling.com/`)
   - Create QR generator utility function
   - Configure error correction and sizing options

2. **QRCodeDisplay Component**
   - Client-side QR code generation using static session ID
   - SVG rendering with responsive sizing
   - Generate QR code once when component mounts (session ID never changes)
   - Error handling for generation failures
   - Accessibility support with alt text and descriptions

3. **QRCodeContainer Component**
   - QR code + participant count display
   - Join instructions text
   - Recent joiners notification
   - Integration with session polling updates

4. **Viewer Layout Integration**
   - Add QR code to viewer session layout
   - Ensure non-intrusive positioning (corner/sidebar)
   - Responsive behavior for different screen sizes
   - Maintain visibility across all activity types

### Step 5: Frontend Mobile Join Interface 
**Files**: `frontend/src/routes/join.tsx`, join form components

1. **Join Route Implementation**
   - Public route `/join/$sessionId` accessible without authentication
   - Mobile-optimized responsive design
   - Deep link support for QR code scanning
   - URL parameter handling for join tokens

2. **ParticipantJoinForm Component**
   - Large, touch-friendly nickname input
   - Real-time nickname validation with debouncing
   - Clear error messaging and success states
   - Loading indicators during join process
   - Automatic redirect after successful join

3. **Mobile Layout Optimization**
   - Touch-friendly interface design
   - Large tap targets and clear typography
   - Optimized for portrait mobile orientation
   - Fast loading and minimal bandwidth usage

### Step 6: Real-time Participant Management
**Files**: Participant hooks, status components, polling integration

1. **useParticipants Hook**
   - Integration with existing polling mechanism
   - Participant list state management
   - Real-time status updates
   - Join/leave event handling

2. **useParticipantJoin Hook**
   - Join flow state management
   - Nickname validation integration
   - Error handling and retry logic
   - Session state synchronization for late joiners

3. **Connection Status Integration**
   - Heartbeat mechanism via polling with activity context sync
   - Automatic status updates (online/offline/disconnected)
   - Activity state synchronization via heartbeat response
   - Connection recovery handling with context restoration
   - Visual indicators for connection state

### Step 7: Admin Interface Integration
**Files**: Admin session route modifications, participant management components

1. **Participant Management Panel**
   - Real-time participant list with status indicators
   - Kick/remove participant functionality
   - Nickname conflict resolution tools
   - Connection status monitoring

2. **Session Management**
   - Late join toggle settings
   - Participant limit configuration
   - Session access controls

## Testing Strategy

### Unit Tests
1. **Backend Service Tests**
   - Participant join flow edge cases
   - Nickname validation logic
   - Heartbeat processing with activity context retrieval
   - Status computation and activity synchronization mechanisms

2. **Frontend Component Tests**
   - QR code display rendering
   - Join form validation behavior
   - Participant list updates
   - Mobile responsive behavior

### Integration Tests
1. **API Endpoint Tests**
   - Complete join flow from QR scan to activity participation
   - Participant heartbeat with activity context synchronization
   - Activity state updates delivered via heartbeat responses
   - Session state synchronization for late joiners
   - Error handling for invalid session IDs and full sessions

2. **Database Integration Tests**
   - Participant model relationships
   - Nickname uniqueness constraints
   - Migration scripts validation
   - Data consistency during concurrent operations

### End-to-End Tests
1. **Mobile Join Flow**
   - QR code scanning simulation
   - Complete join process on mobile viewport
   - Activity state synchronization for late joiners
   - Connection recovery after network interruption

2. **Multi-participant Scenarios**
   - Concurrent participant joining
   - Nickname collision handling
   - Real-time updates across all connected clients
   - Performance with 20+ simultaneous participants

## Deployment Considerations

### Database Migrations
- **Migration Script**: Add participants table with proper indexes
- **Rollback Strategy**: Drop participants table and related session columns
- **Data Integrity**: Ensure foreign key constraints and cascade deletes
- **Performance**: Add indexes for session_id, status, and last_seen queries

### Environment Variables
```bash
# Add to backend environment
MAX_PARTICIPANTS_PER_SESSION=50         # Participant limit
```

### Frontend Configuration
```bash
# QR code settings handled client-side
QR_CODE_BASE_URL=https://app.caja.dbash.dev  # Production join URL base
```

### Frontend Build Configuration
- **Route Configuration**: Ensure public join routes accessible without authentication
- **Asset Optimization**: Optimize QR code SVG rendering for mobile performance
- **Deep Link Handling**: Configure proper URL handling for mobile app deep links

### Performance Monitoring
- **Join Flow Completion Rate**: Track successful vs failed join attempts
- **Participant Status Update Frequency**: Monitor polling overhead with participant tracking
- **Mobile Performance**: Ensure join interface loads quickly on slower networks

## Risk Assessment

### Technical Risks

1. **QR Code Scanning Reliability**
   - **Risk**: Poor scanning success rate on various devices/lighting conditions
   - **Mitigation**: Use high error correction, optimize QR code sizing, provide manual join option
   - **Contingency**: Fall back to manual session ID entry with clear instructions

2. **Mobile Performance**
   - **Risk**: Join interface slow or unresponsive on older mobile devices
   - **Mitigation**: Optimize bundle size, implement progressive loading, minimal dependencies
   - **Contingency**: Provide lightweight text-only join option

3. **Polling Performance Impact**
   - **Risk**: Participant status tracking increases server load significantly
   - **Mitigation**: Optimize database queries, implement participant status caching
   - **Contingency**: Reduce polling frequency or batch participant updates

### Product Risks

1. **Nickname Conflicts and User Experience**
   - **Risk**: Frequent nickname collisions frustrate users during join process
   - **Mitigation**: Smart nickname suggestions, auto-append numbers, clear conflict resolution
   - **Contingency**: Allow duplicate nicknames with internal ID differentiation

2. **Session Capacity Limits**
   - **Risk**: Popular sessions exceed participant limits, causing join failures
   - **Mitigation**: Clear capacity indicators, waiting list functionality, graceful error messages
   - **Contingency**: Dynamic capacity scaling based on session activity type

3. **Late Joiner Experience**
   - **Risk**: Late joiners feel confused or lost when joining mid-activity
   - **Mitigation**: Clear onboarding flow, activity state explanation, catch-up mechanisms
   - **Contingency**: Separate waiting area for late joiners until next activity

### Security Risks

1. **Session Access Control**
   - **Risk**: Unauthorized participants join sessions via leaked QR codes
   - **Mitigation**: Session ID access control, participant moderation, rate limiting
   - **Contingency**: Manual participant approval process for sensitive sessions

2. **Participant Impersonation**
   - **Risk**: Users claim others' nicknames or disrupt sessions with inappropriate names
   - **Mitigation**: Nickname filtering, participant reporting, admin moderation tools
   - **Contingency**: Participant authentication requirement for sensitive use cases

## Estimated Effort

### Development Time Estimates
- **Backend Implementation**: 12-16 hours
  - Database models and migrations: 3-4 hours
  - Service layer implementation: 4-5 hours
  - API endpoints and integration: 3-4 hours
  - Testing and debugging: 2-3 hours

- **Frontend Implementation**: 16-20 hours
  - QR code display components: 4-5 hours
  - Mobile join interface: 6-8 hours
  - Real-time participant management: 4-5 hours
  - Admin interface integration: 2-3 hours

- **Testing and Quality Assurance**: 8-10 hours
  - Unit and integration tests: 4-5 hours
  - End-to-end testing: 2-3 hours
  - Mobile device testing: 2-3 hours

- **Documentation and Polish**: 4-6 hours
  - API documentation updates: 2-3 hours
  - Component documentation: 1-2 hours
  - User guide and screenshots: 1-2 hours

### **Total Estimated Effort: 40-52 hours (5-7 working days)**

### Critical Path Dependencies
1. Database migration must complete before service implementation
2. Backend API endpoints must be functional before frontend integration
3. QR code generation must work before mobile join interface testing
4. Real-time participant tracking depends on polling mechanism updates

### Complexity Assessment
- **Medium-High Complexity**: Multi-device interaction, real-time synchronization, mobile optimization
- **Key Challenges**: Mobile user experience, polling performance, participant state management
- **Success Metrics**: >90% join success rate, <2 second join completion time, stable connection tracking