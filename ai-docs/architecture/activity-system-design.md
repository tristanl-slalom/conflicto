# Activity System Architecture

## Overview

The Caja activity system is designed for maximum flexibility and extensibility, allowing new interactive engagement types to be added without backend modifications. This architecture supports the core principle that activities should be self-contained and define their own data contracts.

## Design Philosophy

### Activity Autonomy Principle
Each activity type is responsible for:
- Defining its own user response data structure
- Implementing its own configuration interface
- Processing and displaying its own results
- Managing its own interaction patterns

### Backend Agnosticism
The backend provides generic services without knowledge of specific activity semantics:
- Activity-agnostic CRUD operations
- Generic JSON storage for user responses
- Standard polling endpoints for real-time updates
- No activity-specific business logic

## Activity Component Architecture

Each activity type implements exactly three React components:

### 1. Configuration Component
**Purpose:** Admin interface for activity setup
**Responsibility:** Define activity parameters and store configuration
**Data Output:** Activity configuration JSON stored in `activities.config`

**Example - Planning Poker Configuration:**
```javascript
const PlanningPokerConfig = {
  activityType: 'planning_poker',
  votingOptions: ['1', '2', '3', '5', '8', '13', '21'],
  allowRevoting: true,
  showVotesRealTime: false,
  timerEnabled: true,
  timerDuration: 300 // seconds
}
```

### 2. Participant Component
**Purpose:** User interaction interface (mobile-optimized)
**Responsibility:** Collect user input and submit responses
**Data Output:** User response JSON stored in `user_responses.response_data`

**Example - Planning Poker Participant Response:**
```javascript
const participantResponse = {
  activityType: 'planning_poker',
  vote: '5',
  votedAt: '2025-10-07T14:30:00Z',
  confidence: 'high',
  notes: 'Based on similar features we built last quarter'
}
```

### 3. Viewer Component
**Purpose:** Real-time results display (large screen optimized)
**Responsibility:** Aggregate responses and display live results
**Data Input:** All user responses for the activity
**Processing:** Client-side aggregation and visualization

**Example - Planning Poker Viewer Processing:**
```javascript
const processVotes = (responses) => {
  const voteCounts = responses.reduce((acc, response) => {
    const vote = response.response_data.vote;
    acc[vote] = (acc[vote] || 0) + 1;
    return acc;
  }, {});

  return {
    totalVotes: responses.length,
    distribution: voteCounts,
    consensus: calculateConsensus(voteCounts),
    averageConfidence: calculateAverageConfidence(responses)
  };
};
```

## Data Flow Architecture

### Configuration Phase
1. Admin opens Configuration Component for activity type
2. Admin specifies activity parameters (questions, options, timing, etc.)
3. Configuration stored as JSON in `activities.config`
4. Activity marked as ready for session

### Participation Phase
1. Participant Component loads activity configuration
2. Component renders interface based on configuration
3. User interacts and submits response
4. Response stored as JSON in `user_responses.response_data`

### Viewing Phase
1. Viewer Component polls for all activity responses
2. Component processes raw JSON responses according to activity logic
3. Aggregated results displayed with real-time updates
4. No backend processing or interpretation required

## Session Configuration vs. Instance Pattern

### Session Configuration (Template)
Defines the blueprint for a session type:
```javascript
const sprintPlanningTemplate = {
  sessionType: 'sprint_planning',
  activities: [
    { type: 'planning_poker', repeatable: true },
    { type: 'confidence_poll', optional: true }
  ],
  defaultDuration: 90, // minutes
  participantLimit: 20
};
```

### Session Instance (Runtime)
Active session with real participants and data:
```javascript
const activeSession = {
  sessionId: 'sess_abc123',
  templateId: 'sprint_planning_v1',
  status: 'active',
  currentActivity: 'planning_poker_1',
  participants: ['p1', 'p2', 'p3'],
  activities: [
    {
      id: 'planning_poker_1',
      type: 'planning_poker',
      status: 'active',
      responses: [...] // User response JSON objects
    }
  ]
};
```

## Database Schema Design

### Core Tables
```sql
-- Session management
sessions (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  template_id VARCHAR(100),
  status session_status,
  admin_id UUID,
  created_at TIMESTAMP
);

-- Activity definitions
activities (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES sessions(id),
  type VARCHAR(50), -- 'planning_poker', 'live_poll', etc.
  config JSONB, -- Activity-specific configuration
  order_index INTEGER,
  status activity_status,
  created_at TIMESTAMP
);

-- Flexible user responses
user_responses (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES sessions(id),
  activity_id UUID REFERENCES activities(id),
  participant_id UUID REFERENCES participants(id),
  response_data JSONB, -- Activity-defined response structure
  created_at TIMESTAMP,
  INDEX (session_id, activity_id) -- Optimized for viewer queries
);
```

### Query Patterns

**Viewer Aggregation Query:**
```sql
SELECT
  participant_id,
  response_data,
  created_at
FROM user_responses
WHERE session_id = $1 AND activity_id = $2
ORDER BY created_at DESC;
```

**Real-time Polling Query:**
```sql
SELECT response_data, created_at
FROM user_responses
WHERE session_id = $1
  AND activity_id = $2
  AND created_at > $3; -- Last poll timestamp
```

## Activity Implementation Examples

### Planning Poker
**Configuration:** Voting options, timer settings, reveal behavior
**Participant:** Card selection interface with confidence rating
**Viewer:** Vote distribution, consensus indicator, timer display

### Live Polling
**Configuration:** Question text, poll options, multiple choice settings
**Participant:** Option selection with optional comments
**Viewer:** Real-time bar chart, percentage breakdown, comment stream

### Word Cloud
**Configuration:** Prompt text, word limits, filtering rules
**Participant:** Text input with character limits
**Viewer:** Dynamic word cloud with size-based frequency display

### Quick Quiz
**Configuration:** Questions, correct answers, timing, scoring
**Participant:** Question display with answer submission
**Viewer:** Leaderboard, correct answer percentages, response speed

## Extension Guidelines

### Adding New Activity Types

1. **Define Data Contract:**
   - Configuration schema for admin setup
   - Response schema for participant input
   - Processing logic for viewer aggregation

2. **Implement Components:**
   - Configuration: Admin setup interface
   - Participant: User interaction interface
   - Viewer: Results display and aggregation

3. **Register Activity Type:**
   - Add to activity type registry
   - Include in admin activity selection
   - Configure routing for components

4. **Testing Strategy:**
   - Mock configuration and response data
   - Test component isolation
   - Validate data contract compliance

### Best Practices

**Configuration Component:**
- Validate configuration before saving
- Provide preview of participant experience
- Include helpful defaults and examples
- Support configuration templates

**Participant Component:**
- Optimize for mobile interaction
- Provide clear submission feedback
- Handle network failures gracefully
- Support offline response queuing

**Viewer Component:**
- Minimize processing on each poll
- Cache aggregation results when possible
- Handle partial response data
- Provide export capabilities for results

## Performance Considerations

### Client-Side Processing Benefits
- Reduces backend computational load
- Allows activity-specific optimization
- Enables rich, interactive visualizations
- Supports offline result processing

### Polling Optimization
- Component-level caching of processed results
- Incremental updates using timestamps
- Efficient JSON processing libraries
- Lazy loading of historical data

### Scalability Pattern
- Activity components scale independently
- Backend remains stateless and generic
- Response aggregation happens at edge (client)
- Database optimized for write-heavy workloads

This architecture enables rapid development of new engagement activities while maintaining system simplicity and performance at scale.
