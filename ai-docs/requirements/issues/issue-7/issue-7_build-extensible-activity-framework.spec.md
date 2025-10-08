# Technical Specification: Build Extensible Activity Framework

**GitHub Issue:** [#7](https://github.com/tristanl-slalom/conflicto/issues/7)
**Generated:** 2025-10-08T13:38:22Z
**Labels:** feature:activity-framework, priority:critical, phase:mvp
**Assignee:** josephc-slalom

## Problem Statement

The Caja live event engagement platform needs a flexible, extensible framework for different types of interactive activities (polls, Q&A, word clouds, etc.). Currently, activities are hard-coded and adding new types requires core system modifications. We need a plugin-based architecture that allows developers to create new activity types without modifying the base framework.

## Technical Requirements

### Field Naming Considerations
- **Metadata Field Naming:** The activity metadata field is named `activity_metadata` in the database schema and SQLAlchemy models to avoid conflicts with SQLAlchemy's own `metadata` attribute, which is used internally by the ORM for table metadata management.

### Universal Persona Support
- **All activities MUST support three personas:** admin, viewer, and participant
- **Admin:** Full control - create, configure, start/stop activities
- **Viewer:** Read-only display - see real-time results and visualizations
- **Participant:** Interactive engagement - submit responses and see feedback

### Core Framework Components

#### 1. Abstract Activity Base Classes
- **Backend:** Abstract `Activity` class with lifecycle methods
- **Frontend:** Base `ActivityComponent` React component interface with persona props
- **Shared:** TypeScript interfaces for activity contracts and persona-specific interfaces

#### 2. Activity Lifecycle State Machine
- **States:** `draft` → `published` → `active` → `expired`
- **Transitions:** Validate state changes with business rules
- **Persistence:** Store state in database with audit trail

#### 3. Activity Type Registry System
- **Discovery:** Static registration of activity types at compile time
- **Registry:** Central registry of available activity types with metadata
- **Loading:** Simple factory pattern for activity instantiation

#### 4. Configuration Schema System
- **Validation:** JSON Schema for activity-specific configurations
- **Types:** TypeScript interfaces generated from schemas
- **Versioning:** Schema migration support for activity updates

### Activity Framework Architecture

```
Activity Framework
├── Core Framework
│   ├── Base Activity Classes
│   ├── State Machine
│   ├── Activity Type Registry
│   └── Configuration Manager
├── Activity Types (Backend)
│   ├── PollingActivity
│   ├── QnaActivity
│   ├── WordCloudActivity
│   └── [Future Activity Classes]
└── Activity Components (Frontend)
    ├── PollingActivity/
    │   ├── PollingAdmin.tsx
    │   ├── PollingViewer.tsx
    │   └── PollingParticipant.tsx
    ├── QnaActivity/
    │   ├── QnaAdmin.tsx
    │   ├── QnaViewer.tsx
    │   └── QnaParticipant.tsx
    └── [Future Activity Components]
```

## API Specifications

### Backend API Endpoints

#### Activity Management
```typescript
// Get available activity types
GET /api/activities/types
Response: ActivityType[]

// Create activity instance
POST /api/sessions/{sessionId}/activities
Body: CreateActivityRequest
Response: Activity

// Update activity configuration
PUT /api/activities/{activityId}
Body: UpdateActivityRequest
Response: Activity

// Transition activity state
POST /api/activities/{activityId}/transition
Body: { target_state: ActivityState, reason?: string }
Response: Activity

// Get activity with current state
GET /api/activities/{activityId}
Response: ActivityWithState

// Get activity responses/data
GET /api/activities/{activityId}/responses
Response: ActivityResponse[]
```

#### Activity Types Management
```typescript
// List available activity types
GET /api/activities/types
Response: ActivityType[]

// Get activity type configuration schema
GET /api/activities/types/{activityType}/schema
Response: JSONSchema
```

### Request/Response Schemas

#### Core Activity Schema
```typescript
interface Activity {
  id: string;
  session_id: string;
  type: string;
  title: string;
  description?: string;
  state: ActivityState;
  configuration: Record<string, unknown>;
  activity_metadata: ActivityMetadata;
  created_at: string;
  updated_at: string;
  expires_at?: string;
}

interface ActivityMetadata {
  duration_seconds?: number;
  max_responses?: number;
  allow_multiple_responses: boolean;
  show_live_results: boolean;
  custom_styling?: Record<string, unknown>;
}

type ActivityState = 'draft' | 'published' | 'active' | 'expired';

interface ActivityType {
  id: string;
  name: string;
  description: string;
  version: string;
  schema: JSONSchema;
}
```

#### Activity Type Definition Interface
```typescript
interface ActivityType {
  id: string;
  name: string;
  version: string;
  description: string;
  schema: JSONSchema;
}

interface ActivityTypeRegistry {
  [activityType: string]: {
    class: typeof BaseActivity;
    schema: JSONSchema;
    metadata: ActivityType;
  };
}
```

## Data Models

### Database Schema

#### Activities Table
```sql
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id),
    type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    state activity_state_enum NOT NULL DEFAULT 'draft',
    configuration JSONB NOT NULL DEFAULT '{}',
    activity_metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT valid_configuration CHECK (jsonb_typeof(configuration) = 'object'),
    CONSTRAINT valid_activity_metadata CHECK (jsonb_typeof(activity_metadata) = 'object')
);

CREATE TYPE activity_state_enum AS ENUM ('draft', 'published', 'active', 'expired');
```

#### Activity Responses Table
```sql
CREATE TABLE activity_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id UUID NOT NULL REFERENCES activities(id),
    user_id UUID REFERENCES users(id),
    session_participant_id UUID REFERENCES session_participants(id),
    response_data JSONB NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_response_data CHECK (jsonb_typeof(response_data) = 'object')
);
```

### SQLAlchemy Models
Located in `/backend/app/db/models.py`:

```python
class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    type: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    state: Mapped[ActivityState] = mapped_column(Enum(ActivityState), default=ActivityState.DRAFT)
    configuration: Mapped[dict] = mapped_column(JSONB, default=dict)
    activity_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="activities")
    responses: Mapped[list["ActivityResponse"]] = relationship("ActivityResponse", back_populates="activity")
```

## Interface Requirements

### Universal Multi-Persona Support
**CRITICAL:** Every activity type MUST provide components for all three personas. The framework will automatically render the appropriate persona interface based on user context.

### Multi-Persona UI Components

#### Admin Interface Requirements (Required for ALL activities)
- **Activity Configuration:** Form-based configuration using plugin schemas
- **State Management:** Controls to transition activity states
- **Live Monitoring:** Real-time activity status and participant engagement
- **Content Management:** Text editing for activity content

#### Viewer Interface Requirements (Required for ALL activities)
- **Large Screen Display:** Optimized for projection/large monitors
- **Live Results:** Real-time visualization of activity responses
- **QR Code Generation:** Dynamic QR codes for participant access
- **Progress Indicators:** Visual activity timeline and progress

#### Participant Interface Requirements (Required for ALL activities)
- **Mobile-First Design:** Optimized for smartphones and tablets
- **Touch-Friendly Controls:** Large buttons and intuitive gestures
- **Cross-Browser:** Support for iOS Safari, Android Chrome

### Component Architecture
```typescript
// Base component interfaces - ALL activity types must implement all three persona components
interface BaseActivityComponent<TConfig = unknown> {
  activity: Activity;
  configuration: TConfig;
  onStateChange: (newState: ActivityState) => void;
}

interface AdminActivityComponent<TConfig = unknown> extends BaseActivityComponent<TConfig> {
  onConfigUpdate: (config: TConfig) => void;
  onSave: () => void;
  validation: ValidationResult;
}

interface ViewerActivityComponent<TConfig = unknown> extends BaseActivityComponent<TConfig> {
  responses: ActivityResponse[];
  liveResults: boolean;
}

interface ParticipantActivityComponent<TConfig = unknown> extends BaseActivityComponent<TConfig> {
  onSubmitResponse: (response: unknown) => void;
  canSubmit: boolean;
  hasSubmitted: boolean;
}
```

## Integration Points

### Session Integration
- **Session Context:** Activities inherit session permissions and settings
- **Session Lifecycle:** Activities are bound to session lifecycle
- **Participant Management:** Leverage existing session participant system
- **Real-time Polling:** Use existing 2-3 second polling mechanism

### Authentication & Authorization
- **Admin Access:** Session organizers can manage activities
- **Viewer Access:** Public access for viewer displays
- **Participant Access:** Anonymous participant access

### External Services
- **Analytics:** Activity engagement metrics and reporting
- **Notifications:** Real-time updates via polling system
- **Caching:** Redis for activity state and response caching

## Acceptance Criteria

### Technical Acceptance Criteria

#### Framework Foundation
- [ ] Abstract base classes implemented for activities
- [ ] State machine handles all activity lifecycle transitions
- [ ] Activity type registry system with static registration at startup
- [ ] JSON schema validation works for activity configurations
- [ ] Database models support extensible activity data

#### Activity Type Architecture
- [ ] New activity types can be added by creating new classes and registering them
- [ ] Activity type registry provides easy lookup and instantiation
- [ ] Activity schemas are validated at compile time using TypeScript
- [ ] Type-safe interfaces for all activity types
- [ ] Clear pattern for adding new activity types
- [ ] Registration system validates that all three persona components exist before accepting a new activity type

#### Universal Multi-Persona Support
- [ ] ALL activity types implement admin, viewer, AND participant components
- [ ] Admin components support activity configuration for all types
- [ ] Viewer components display live results appropriately for all types
- [ ] Participant components work on mobile devices for all types
- [ ] All personas have consistent user experience
- [ ] Component interfaces are properly typed

#### State Management
- [ ] Activities transition through states correctly
- [ ] State changes are validated and audited
- [ ] Expired activities are handled gracefully
- [ ] Concurrent state changes are managed safely
- [ ] State persistence survives system restarts

#### API Completeness
- [ ] All CRUD operations available for activities
- [ ] Activity responses can be submitted and retrieved
- [ ] Activity type metadata accessible via API
- [ ] State transitions logged and auditable
- [ ] API documentation is complete and accurate

## Assumptions & Constraints

### Technical Assumptions
- **Polling-Based Sync:** No WebSockets for MVP, using 2-3 second polling
- **JSON Configuration:** Activity configs stored as JSONB in PostgreSQL
- **React Framework:** Frontend uses React with TypeScript
- **FastAPI Backend:** Backend uses FastAPI with SQLAlchemy
- **Static Registration:** Activity types registered at compile time, no dynamic loading

### Business Constraints
- **Session Scope:** Activities are scoped to sessions, not global
- **Participant Limits:** Support up to 50+ concurrent participants per activity
- **Mobile First:** Participant experience must work on mobile devices
- **MVP Timeline:** Core framework needed for Phase 1 MVP
- **No Real-time:** Polling-based updates only, no WebSocket requirements

### Performance Constraints
- **Response Time:** API responses under 200ms for activity operations
- **Concurrent Users:** Support 50+ concurrent users per session
- **Database Performance:** Efficient queries for activity and response data
- **Plugin Loading:** Plugin discovery and loading under 1 second
- **Memory Usage:** Reasonable memory footprint for plugin registry

### Security Constraints
- **Input Validation:** All activity configurations validated against schemas
- **SQL Injection:** Parameterized queries for all database operations
- **XSS Prevention:** Sanitized output for activity content and responses
- **Code Safety:** All activity types are compiled into the application
- **Access Control:** Proper authorization for activity management operations
