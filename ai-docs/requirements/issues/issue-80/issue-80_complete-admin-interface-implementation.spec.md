# Technical Specification: Complete Admin Interface Implementation for Activity & Session Management

**GitHub Issue:** [#80](https://github.com/tristanl-slalom/conflicto/issues/80)
**Generated:** October 8, 2025

## Problem Statement

The admin interface currently supports basic session creation and listing, but lacks critical functionality for complete session and activity management. The missing components prevent end-to-end session workflows and block integration testing of the complete Caja platform. Key gaps include activity management integration, session lifecycle controls, real-time updates, and participant management.

## Technical Requirements

### 1. Activity Management System Integration
- Integrate existing `ActivityManagement` component into admin interface
- Implement API calls for creating activities within sessions
- Connect activity framework (PollingActivity, Q&A, Word Cloud) to admin UI
- Add activity configuration interface for each activity type
- Implement activity ordering and management within sessions

### 2. Session Lifecycle Controls
- Start/Stop/Pause session controls with proper state validation
- Session status transitions following draft → active → completed flow
- Activity sequencing controls for managing activity order
- Session state validation before allowing transitions
- Proper error handling for invalid state changes

### 3. Real-time Updates & Polling Implementation
- Real-time session participant count updates
- Activity response count updates during live sessions
- Live session status monitoring with automatic refresh
- Implement polling-based synchronization (2-3 second intervals)
- Graceful handling of network interruptions and offline states

### 4. QR Code & Participant Management
- QR code generation and display for participant joining
- Participant join URL generation and management
- Live participant list display in admin interface
- Participant management controls (view, remove if needed)

## API Specifications

### Activity Management Endpoints
```typescript
// Create activity within session
POST /api/v1/sessions/{id}/activities
Request: {
  type: 'poll' | 'qna' | 'word_cloud';
  title: string;
  description?: string;
  configuration: ActivityConfiguration;
  order: number;
}
Response: Activity

// Update activity order
PUT /api/v1/sessions/{id}/activities/{activityId}/order
Request: { order: number }
Response: Activity

// Get session activities
GET /api/v1/sessions/{id}/activities
Response: Activity[]
```

### Session Lifecycle Endpoints
```typescript
// Update session status
PUT /api/v1/sessions/{id}/status
Request: {
  status: 'draft' | 'active' | 'paused' | 'completed';
  force?: boolean; // Override validation checks
}
Response: Session

// Get session with real-time data
GET /api/v1/sessions/{id}/live
Response: {
  session: Session;
  participantCount: number;
  activeActivity?: Activity;
  activityResponses?: number;
}
```

### Participant Management Endpoints
```typescript
// Get session participants
GET /api/v1/sessions/{id}/participants
Response: {
  participants: Participant[];
  count: number;
  joinUrl: string;
  qrCodeData: string;
}
```

## Data Models

### Enhanced Session Model
```typescript
interface Session {
  id: string;
  title: string;
  description?: string;
  status: SessionStatus;
  qr_code: string;
  admin_code: string;
  join_url: string;
  activities: Activity[];
  participant_count: number;
  created_at: string;
  updated_at: string;
  started_at?: string;
  completed_at?: string;
}

enum SessionStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed'
}
```

### Activity Configuration Models
```typescript
interface BaseActivityConfiguration {
  type: ActivityType;
  title: string;
  description?: string;
  order: number;
  time_limit?: number;
}

interface PollingConfiguration extends BaseActivityConfiguration {
  type: 'poll';
  question: string;
  options: string[];
  multiple_choice: boolean;
  anonymous: boolean;
}

interface QnaConfiguration extends BaseActivityConfiguration {
  type: 'qna';
  prompt: string;
  anonymous: boolean;
  moderation_required: boolean;
}

interface WordCloudConfiguration extends BaseActivityConfiguration {
  type: 'word_cloud';
  prompt: string;
  max_words: number;
  min_word_length: number;
}
```

### Participant Model
```typescript
interface Participant {
  id: string;
  session_id: string;
  display_name?: string;
  joined_at: string;
  last_seen: string;
  is_active: boolean;
}
```

## Interface Requirements

### Updated Admin Interface Layout
```
AdminDashboard
├── SessionList (existing)
├── SessionCreation (existing)
└── SessionManagement (enhanced)
    ├── SessionControls (new)
    ├── ActivityManagement (integrate existing)
    ├── ParticipantManagement (new)
    └── QRCodeDisplay (new)
```

### New Component Requirements

#### SessionControls Component
- Start/Pause/Stop session buttons with proper state validation
- Session status indicator with visual feedback
- Activity sequencing controls (next/previous activity)
- Session timer display for active sessions
- Validation warnings for state transitions

#### ParticipantManagement Component
- Live participant count with auto-refresh
- Participant list with join times and activity status
- QR code display with proper sizing and styling
- Join URL copy functionality
- Participant management actions

#### Enhanced ActivityManagement Component
- Activity type selection (Poll, Q&A, Word Cloud)
- Type-specific configuration forms
- Activity ordering with drag-and-drop or controls
- Activity status tracking during sessions
- Preview functionality for each activity type

### Mobile Responsiveness Requirements
- Admin interface optimized for desktop/tablet use
- QR codes properly sized for mobile scanning
- Responsive layout for different screen sizes
- Touch-friendly controls for activity management

## Integration Points

### Frontend Integration Points
- TanStack Query for API state management and caching
- Activity registry for dynamic activity component loading
- Real-time polling hooks for live data updates
- Session context provider for shared session state

### Backend Integration Points
- FastAPI route handlers for new endpoints
- SQLAlchemy models for activity and participant data
- Session state validation middleware
- Activity framework plugin system integration

### External Dependencies
- QR code generation library (existing backend implementation)
- Polling mechanism for real-time updates (no WebSockets)
- Activity framework components (PollingAdmin, etc.)

## Acceptance Criteria

### Session Management
- [ ] Admin can create, start, pause, and end sessions
- [ ] Session status is clearly displayed and updates in real-time
- [ ] Cannot start session without at least one activity
- [ ] Session lifecycle follows proper state transitions (draft → active → paused → completed)
- [ ] Proper error messages for invalid state transitions

### Activity Management
- [ ] Admin can add activities to sessions (Poll, Q&A, Word Cloud)
- [ ] Each activity type has proper configuration UI with validation
- [ ] Activities can be reordered within sessions
- [ ] Activity status is tracked and displayed during sessions
- [ ] Activity configuration is saved and retrievable

### Participant Experience
- [ ] QR codes are displayed clearly for easy participant joining
- [ ] Live participant count shows in admin interface with auto-refresh
- [ ] Admin can view active participants with join times
- [ ] Join URLs are easily accessible and copyable

### Real-time Updates
- [ ] Session data refreshes automatically every 2-3 seconds
- [ ] Activity responses update live during active sessions
- [ ] Participant count updates when users join/leave
- [ ] Network interruptions are handled gracefully

### Performance Requirements
- [ ] Admin interface remains responsive with 50+ concurrent participants
- [ ] Polling overhead is minimized through efficient caching
- [ ] Large participant lists are paginated or virtualized
- [ ] QR code rendering is optimized for quick display

## Assumptions & Constraints

### Technical Assumptions
- Backend APIs for session lifecycle management exist and are functional
- Activity framework components are complete and stable
- QR code generation is handled by backend
- Polling-based synchronization is sufficient for MVP (no WebSockets required)

### Business Constraints
- Admin interface is desktop/tablet focused (mobile-friendly but not mobile-first)
- Real-time updates use polling with 2-3 second intervals maximum
- Session participant limit is 50+ concurrent users
- Activity types are limited to Poll, Q&A, and Word Cloud for MVP

### Development Constraints
- Must maintain TypeScript strict mode compliance
- Follow existing admin UI patterns and component structure
- Integration with existing session creation and listing functionality
- Backward compatibility with existing session data
