# Technical Specification: Pre-Lobby Landing Page for Draft Sessions with Live Attendee List

**GitHub Issue:** [#78](https://github.com/tristanl-slalom/conflicto/issues/78)
**Generated:** 2025-10-08T20:45:00Z

## Problem Statement

When participants scan a QR code and join a session that is still in `draft` status, they don't have a clear interface showing who else is present and waiting. This creates a poor user experience where participants are unsure if the session is active or if other attendees are present.

The need is for a "waiting room" experience that builds anticipation and allows participants to see other attendees before the session officially starts.

## Technical Requirements

### Frontend Components

#### PreLobbyLandingPage Component
- **Purpose**: Display landing page for sessions in `draft` status
- **Scope**: Replace current participant interface when session status is `draft`
- **Key Features**:
  - Session information display (title, description)
  - Real-time participant list with nicknames and online status
  - Participant count prominently displayed
  - Session status indicator showing "Waiting for session to start"
  - Auto-refresh/polling for participant updates
  - Clean, welcoming design matching existing UI patterns

#### Real-time Participant List Integration
- **Polling Mechanism**: Leverage existing `ParticipantList` component patterns
- **Update Frequency**: Follow existing 2-3 second polling intervals
- **Status Indicators**: Green dot for online, amber for idle, gray for disconnected
- **Data Display**: Show participant nicknames

### Backend Integration

#### API Endpoints (Existing)
- `GET /api/v1/sessions/{session_id}/participants` - Retrieve participant list
- `GET /api/v1/sessions/{session_id}` - Session details including status
- `POST /api/v1/sessions/{session_id}/join` - Join session (works for draft sessions)
- `POST /api/v1/participants/{participant_id}/heartbeat` - Maintain participant presence
- Existing participant status computation (`online`, `idle`, `disconnected`)

#### Backend Considerations for Draft Sessions

##### Participant Join Flow for Draft Sessions
- **Current Behavior**: Participants can already join draft sessions without restrictions
- **Session State Response**: `_get_session_state()` already includes `session_status` 
- **Activity Context**: Handle `current_activity: null` for draft sessions appropriately
- **No Backend Changes Required**: Existing participant service handles draft sessions correctly

##### Session Status Transition Handling
- **Status Polling**: Existing session status is included in participant heartbeat responses
- **Activity Context Updates**: When session transitions to active, participants get updated activity context
- **Real-time Awareness**: Participants in pre-lobby will detect status changes through existing polling

##### Data Consistency Considerations
- **Participant Persistence**: Participants joined during draft persist through status transitions
- **Heartbeat Continuity**: Existing heartbeat mechanism continues working across status changes
- **Session Cleanup**: Existing participant cleanup mechanisms remain unchanged

## API Specifications

### Existing API Utilization

#### Session Details Endpoint
```
GET /api/v1/sessions/{session_id}
Response: {
  "id": number,
  "title": string,
  "description": string | null,
  "status": "draft" | "active" | "completed",
  "participant_count": number,
  ...
}
```

#### Participants List Endpoint
```
GET /api/v1/sessions/{session_id}/participants
Response: {
  "participants": [
    {
      "participant_id": string,
      "nickname": string,
      "status": "online" | "idle" | "disconnected",
      "joined_at": datetime,
      "last_seen": datetime
    }
  ],
  "total_count": number
}
```

#### Participant Join Endpoint (Already Supports Draft Sessions)
```
POST /api/v1/sessions/{session_id}/join
Request: {
  "nickname": string
}
Response: {
  "participant_id": string,
  "session_state": {
    "session_id": number,
    "session_title": string,
    "session_status": "draft" | "active" | "completed",
    "current_activity": null | ActivityObject,  // null for draft sessions
    "participant_count": number
  }
}
```

#### Participant Heartbeat Endpoint (Includes Session Status)
```
POST /api/v1/participants/{participant_id}/heartbeat
Request: {
  "timestamp": datetime
}
Response: {
  "status": "online" | "idle" | "disconnected",
  "activity_context": {
    "session_status": "draft" | "active" | "completed",
    "current_activity": null | ActivityObject  // Updated when session becomes active
  },
  "updated_at": datetime
}
```

## Data Models

### Existing Models Utilized

#### SessionDetail Model
- `id`: Session identifier
- `title`: Session title for display
- `description`: Optional session description
- `status`: Session status (`draft`, `active`, `completed`)
- `participant_count`: Current participant count

#### ParticipantStatus Model
- `participant_id`: Unique participant identifier
- `nickname`: Display name for participant
- `status`: Computed status (`online`, `idle`, `disconnected`)
- `joined_at`: Timestamp when participant joined
- `last_seen`: Last heartbeat timestamp

## Interface Requirements

### UI/UX Specifications

#### Layout Design
- **Mobile-first**: Optimized for QR code scanning devices
- **Responsive Design**: Adaptable to various screen sizes
- **Welcoming Interface**: Clean, anticipatory design language
- **Status Clarity**: Clear messaging that session hasn't started yet

#### Visual Elements
- **Session Header**: Prominent session title and description
- **Participant Count**: Large, visible participant counter
- **Status Indicator**: Clear "Waiting for session to start" message
- **Participant Grid**: List of participants with status indicators
- **Loading States**: Smooth transitions during updates

#### Accessibility
- **WCAG 2.1 AA Compliance**: Proper contrast ratios and keyboard navigation
- **Screen Reader Support**: Semantic HTML and ARIA labels
- **Touch Targets**: Minimum 44px touch targets for mobile

## Integration Points

### Existing System Integration

#### Participant Management System
- Integrate with existing `ParticipantService` for status computation
- Utilize current heartbeat mechanism for participant status
- Leverage existing participant join/leave flows

#### Session State Management
- Use existing `useSession` hooks for session data fetching
- Implement session status-based routing logic
- Integrate with current session lifecycle management

#### Real-time Polling Infrastructure
- Utilize existing TanStack Query polling patterns
- Follow established 2-3 second polling intervals
- Implement optimistic updates with conflict resolution

## Acceptance Criteria

### Functional Requirements
1. **Draft Session Detection**: When a participant joins a session in `draft` status, display the pre-lobby landing page
2. **Real-time Participant List**: Display all participants currently in the lobby with real-time updates
3. **Live Updates**: Participant list updates within polling interval (2-3 seconds) when new participants join
4. **Status Accuracy**: Participant status (online/idle/disconnected) reflects accurately
5. **Session Transition**: When session transitions from `draft` to `active`, participants automatically move to active session interface

### Technical Requirements
1. **Mobile Responsive**: Interface works seamlessly on mobile devices (QR code users)
2. **Performance**: Polling performs efficiently with 50+ concurrent participants
3. **Error Handling**: Graceful handling of network interruptions and API failures
4. **Accessibility**: Meets WCAG 2.1 AA standards

### User Experience Requirements
1. **Clear Messaging**: Participants understand they're in a waiting state
2. **Social Proof**: Participants can see other attendees building confidence
3. **Seamless Transition**: Smooth transition to active session when it starts
4. **Consistent Design**: Matches existing Caja design system patterns

## Assumptions & Constraints

### Technical Assumptions
- Existing participant management API is stable and performant
- Current polling infrastructure can handle pre-lobby traffic
- Session status transitions are reliable and immediate
- QR code scanning flow delivers participants to correct join route

### Design Constraints
- Must maintain consistency with existing Caja UI patterns
- Mobile-first design for QR code scanning use cases
- Polling-based updates (no WebSocket implementation)
- Integration with existing participant heartbeat system

### Performance Constraints
- Support for 50+ concurrent participants in pre-lobby
- Polling frequency limited to 2-3 second intervals
- Efficient database queries for participant status computation
- Minimal bandwidth usage for mobile participants

### Business Constraints
- Feature should not disrupt existing session management flows
- Implementation should leverage existing APIs without modification
- Must support seamless transition to active session state
- Should enhance participant engagement without adding complexity