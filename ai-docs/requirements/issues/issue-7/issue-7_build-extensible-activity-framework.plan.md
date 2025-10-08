# Implementation Plan: Build Extensible Activity Framework

**GitHub Issue:** [#7](https://github.com/tristanl-slalom/conflicto/issues/7)  
**Generated:** 2025-10-08T15:45:00Z  
**Labels:** feature:activity-framework, priority:critical, phase:mvp  
**Assignee:** josephc-slalom

## Overview

This plan implements a static, extensible activity framework that allows easy addition of new activity types without core system modifications. All activities support universal personas (admin/viewer/participant) with activity-centric component organization.

## Phase 1: Backend Framework Foundation

### Step 1: Database Schema Updates
**Files:** `backend/migrations/versions/`, `backend/app/db/models.py`, `backend/app/db/enums.py`

Update the existing Activity model to support the framework:

```python
# Add to backend/app/db/enums.py
class ActivityState(str, Enum):
    """Enhanced activity state enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published" 
    ACTIVE = "active"
    EXPIRED = "expired"

# Update backend/app/db/models.py - enhance existing Activity model
class Activity(Base):
    # Update existing fields
    title: Mapped[str] = mapped_column(String(500))  # Increase from current length
    state: Mapped[str] = mapped_column(String(20), default="draft")  # Use ActivityState enum values
    metadata: Mapped[dict] = mapped_column(JSONBType, default=dict)  # New field for framework metadata
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))  # New field
```

Create migration for schema updates:
```sql
-- Add new columns to activities table
ALTER TABLE activities ADD COLUMN metadata JSONB DEFAULT '{}';
ALTER TABLE activities ADD COLUMN expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE activities ALTER COLUMN title TYPE VARCHAR(500);
```

### Step 2: Activity Base Classes and Registry
**Files:** `backend/app/services/activity_framework/`

Create the core framework classes:

```python
# backend/app/services/activity_framework/__init__.py
from .base import BaseActivity
from .registry import ActivityRegistry
from .state_machine import ActivityStateMachine

# backend/app/services/activity_framework/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class BaseActivity(ABC):
    """Abstract base class for all activity types."""
    
    def __init__(self, activity_id: UUID, config: Dict[str, Any]):
        self.activity_id = activity_id
        self.config = config
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate activity configuration."""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for activity configuration."""
        pass
    
    @abstractmethod
    def can_transition_to(self, target_state: str) -> bool:
        """Check if activity can transition to target state."""
        pass
    
    @abstractmethod
    def process_response(self, participant_id: int, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate participant response."""
        pass

# backend/app/services/activity_framework/registry.py
from typing import Dict, Type, Any
from .base import BaseActivity

class ActivityRegistry:
    """Registry for activity types."""
    
    _registry: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register(cls, activity_type: str, activity_class: Type[BaseActivity], schema: Dict[str, Any]):
        """Register an activity type."""
        cls._registry[activity_type] = {
            'class': activity_class,
            'schema': schema,
            'name': activity_type.replace('_', ' ').title()
        }
    
    @classmethod
    def get_activity_class(cls, activity_type: str) -> Type[BaseActivity]:
        """Get activity class for type."""
        if activity_type not in cls._registry:
            raise ValueError(f"Unknown activity type: {activity_type}")
        return cls._registry[activity_type]['class']
    
    @classmethod
    def get_all_types(cls) -> Dict[str, Dict[str, Any]]:
        """Get all registered activity types."""
        return cls._registry.copy()
```

### Step 3: State Machine Implementation
**Files:** `backend/app/services/activity_framework/state_machine.py`

```python
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime

class ActivityStateMachine:
    """Manages activity state transitions."""
    
    # Valid state transitions
    TRANSITIONS = {
        'draft': ['published'],
        'published': ['active', 'draft'],
        'active': ['expired'],
        'expired': []  # Terminal state
    }
    
    @classmethod
    def can_transition(cls, current_state: str, target_state: str) -> bool:
        """Check if transition is valid."""
        return target_state in cls.TRANSITIONS.get(current_state, [])
    
    @classmethod
    def transition(cls, activity, target_state: str, reason: Optional[str] = None) -> bool:
        """Perform state transition."""
        if not cls.can_transition(activity.state, target_state):
            return False
        
        activity.state = target_state
        activity.updated_at = datetime.utcnow()
        
        # Set expires_at when activating
        if target_state == 'active' and activity.metadata.get('duration_seconds'):
            duration = activity.metadata['duration_seconds']
            activity.expires_at = datetime.utcnow() + timedelta(seconds=duration)
        
        return True
```

### Step 4: Activity Service Enhancement
**Files:** `backend/app/services/activity_service.py`

Update existing ActivityService to use the framework:

```python
# Enhance the existing service with framework integration
from app.services.activity_framework import ActivityRegistry, ActivityStateMachine, BaseActivity

class ActivityService:
    # Add to existing methods
    
    async def create_activity(self, session_id: int, activity_data: ActivityCreate) -> Activity:
        """Create activity using framework."""
        # Validate activity type is registered
        if activity_data.activity_type not in ActivityRegistry.get_all_types():
            raise ValueError(f"Unknown activity type: {activity_data.activity_type}")
        
        # Get activity class and validate configuration
        activity_class = ActivityRegistry.get_activity_class(activity_data.activity_type)
        activity_instance = activity_class(None, activity_data.configuration)
        
        if not activity_instance.validate_config(activity_data.configuration):
            raise ValueError("Invalid activity configuration")
        
        # Create database record (enhance existing create method)
        db_activity = Activity(
            session_id=session_id,
            type=activity_data.activity_type,
            title=activity_data.title,
            description=activity_data.description,
            config=activity_data.configuration,
            order_index=activity_data.order_index,
            metadata=getattr(activity_data, 'metadata', {}),
            state='draft'
        )
        
        # Use existing database operations
        self.db.add(db_activity)
        await self.db.commit()
        await self.db.refresh(db_activity)
        
        return db_activity
    
    async def transition_activity_state(self, activity_id: UUID, target_state: str, reason: Optional[str] = None) -> Activity:
        """Transition activity state using state machine."""
        activity = await self.get_activity(activity_id)
        
        if not ActivityStateMachine.can_transition(activity.state, target_state):
            raise ValueError(f"Cannot transition from {activity.state} to {target_state}")
        
        if ActivityStateMachine.transition(activity, target_state, reason):
            await self.db.commit()
            await self.db.refresh(activity)
        
        return activity
```

## Phase 2: Concrete Activity Types

### Step 5: Polling Activity Implementation
**Files:** `backend/app/services/activity_types/`

```python
# backend/app/services/activity_types/__init__.py
from .polling import PollingActivity
from .qna import QnaActivity
from .word_cloud import WordCloudActivity

# backend/app/services/activity_types/polling.py
from app.services.activity_framework.base import BaseActivity
from typing import Dict, Any
import json

class PollingActivity(BaseActivity):
    """Polling/Survey activity implementation."""
    
    SCHEMA = {
        "type": "object",
        "properties": {
            "question": {"type": "string", "minLength": 1, "maxLength": 500},
            "options": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 10
            },
            "allow_multiple_choice": {"type": "boolean", "default": False},
            "show_live_results": {"type": "boolean", "default": True}
        },
        "required": ["question", "options"]
    }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate polling configuration."""
        try:
            # Basic validation - in production use jsonschema library
            return (
                'question' in config and 
                'options' in config and 
                len(config['options']) >= 2
            )
        except Exception:
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema."""
        return self.SCHEMA
    
    def can_transition_to(self, target_state: str) -> bool:
        """Check state transition validity."""
        # Polling activities can use default transitions
        return True
    
    def process_response(self, participant_id: int, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process polling response."""
        selected_options = response_data.get('selected_options', [])
        
        # Validate response
        if not isinstance(selected_options, list):
            raise ValueError("Invalid response format")
        
        if not self.config.get('allow_multiple_choice') and len(selected_options) > 1:
            raise ValueError("Multiple choices not allowed")
        
        return {
            'participant_id': participant_id,
            'selected_options': selected_options,
            'timestamp': datetime.utcnow().isoformat()
        }
```

### Step 6: Q&A Activity Implementation
**Files:** `backend/app/services/activity_types/qna.py`

```python
class QnaActivity(BaseActivity):
    """Q&A activity implementation."""
    
    SCHEMA = {
        "type": "object", 
        "properties": {
            "topic": {"type": "string", "minLength": 1, "maxLength": 200},
            "allow_anonymous": {"type": "boolean", "default": True},
            "enable_voting": {"type": "boolean", "default": True},
            "moderate_questions": {"type": "boolean", "default": False}
        },
        "required": ["topic"]
    }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Q&A configuration."""
        return 'topic' in config and len(config['topic'].strip()) > 0
    
    def process_response(self, participant_id: int, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Q&A response (question submission or vote)."""
        response_type = response_data.get('type')
        
        if response_type == 'question':
            return {
                'type': 'question',
                'participant_id': participant_id,
                'question_text': response_data.get('question_text', ''),
                'timestamp': datetime.utcnow().isoformat()
            }
        elif response_type == 'vote':
            return {
                'type': 'vote', 
                'participant_id': participant_id,
                'question_id': response_data.get('question_id'),
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            raise ValueError("Invalid response type")
```

### Step 7: Activity Type Registration
**Files:** `backend/app/main.py`, `backend/app/services/activity_framework/registration.py`

```python
# backend/app/services/activity_framework/registration.py
from .registry import ActivityRegistry
from ..activity_types.polling import PollingActivity
from ..activity_types.qna import QnaActivity
from ..activity_types.word_cloud import WordCloudActivity

def register_activity_types():
    """Register all activity types at startup."""
    ActivityRegistry.register('poll', PollingActivity, PollingActivity.SCHEMA)
    ActivityRegistry.register('qna', QnaActivity, QnaActivity.SCHEMA)
    ActivityRegistry.register('word_cloud', WordCloudActivity, WordCloudActivity.SCHEMA)

# Add to backend/app/main.py startup
from app.services.activity_framework.registration import register_activity_types

@app.on_event("startup")
async def startup_event():
    register_activity_types()
    # ... existing startup code
```

## Phase 3: API Routes Enhancement

### Step 8: Activity Routes Enhancement
**Files:** `backend/app/routes/activities.py`

Enhance existing routes with framework support:

```python
# Add to existing routes/activities.py
from app.services.activity_framework import ActivityRegistry

@router.get("/types")
async def get_activity_types():
    """Get all available activity types."""
    types = ActivityRegistry.get_all_types()
    return [
        {
            'id': type_id,
            'name': info['name'],
            'schema': info['schema']
        }
        for type_id, info in types.items()
    ]

@router.get("/types/{activity_type}/schema")
async def get_activity_schema(activity_type: str):
    """Get JSON schema for activity type."""
    if activity_type not in ActivityRegistry.get_all_types():
        raise HTTPException(status_code=404, detail="Activity type not found")
    
    activity_class = ActivityRegistry.get_activity_class(activity_type)
    return activity_class.SCHEMA

@router.post("/{activity_id}/transition")
async def transition_activity_state(
    activity_id: UUID,
    transition_request: ActivityTransitionRequest,
    activity_service: ActivityService = Depends(get_activity_service)
):
    """Transition activity state."""
    try:
        activity = await activity_service.transition_activity_state(
            activity_id, 
            transition_request.target_state,
            transition_request.reason
        )
        return activity
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Step 9: Schema Updates
**Files:** `backend/app/models/schemas.py`

Add new Pydantic models for framework:

```python
# Add to existing schemas.py
class ActivityTransitionRequest(BaseModel):
    """Activity state transition request."""
    target_state: str = Field(..., pattern="^(draft|published|active|expired)$")
    reason: Optional[str] = Field(None, max_length=500)

class ActivityTypeResponse(BaseModel):
    """Activity type information response."""
    id: str
    name: str
    description: str
    schema: Dict[str, Any]

class ActivityWithStateResponse(ActivityResponse):
    """Activity response with enhanced state info."""
    state: str
    expires_at: Optional[datetime]
    metadata: Dict[str, Any] = {}
```

## Phase 4: Frontend Framework

### Step 10: Activity Component Base Classes
**Files:** `frontend/src/components/activities/`

```typescript
// frontend/src/components/activities/base/ActivityTypes.ts
export interface BaseActivityProps {
  activity: Activity;
  configuration: Record<string, unknown>;
  onStateChange: (newState: ActivityState) => void;
}

export interface AdminActivityProps extends BaseActivityProps {
  onConfigUpdate: (config: Record<string, unknown>) => void;
  onSave: () => void;
  validation?: ValidationResult;
}

export interface ViewerActivityProps extends BaseActivityProps {
  responses: ActivityResponse[];
  liveResults: boolean;
}

export interface ParticipantActivityProps extends BaseActivityProps {
  onSubmitResponse: (response: unknown) => void;
  canSubmit: boolean;
  hasSubmitted: boolean;
}

// frontend/src/components/activities/base/BaseActivity.tsx
export abstract class BaseActivityComponent<TConfig = Record<string, unknown>> {
  abstract renderAdmin(props: AdminActivityProps): React.ReactElement;
  abstract renderViewer(props: ViewerActivityProps): React.ReactElement; 
  abstract renderParticipant(props: ParticipantActivityProps): React.ReactElement;
}
```

### Step 11: Activity Registry (Frontend)
**Files:** `frontend/src/lib/activityRegistry.ts`

```typescript
import { BaseActivityComponent } from '@/components/activities/base/BaseActivity';
import { PollingActivity } from '@/components/activities/PollingActivity';
import { QnaActivity } from '@/components/activities/QnaActivity';
import { WordCloudActivity } from '@/components/activities/WordCloudActivity';

export interface ActivityTypeDefinition {
  id: string;
  name: string;
  component: typeof BaseActivityComponent;
}

class ActivityRegistry {
  private registry = new Map<string, ActivityTypeDefinition>();
  
  register(id: string, name: string, component: typeof BaseActivityComponent) {
    this.registry.set(id, { id, name, component });
  }
  
  get(activityType: string): ActivityTypeDefinition | undefined {
    return this.registry.get(activityType);
  }
  
  getAll(): ActivityTypeDefinition[] {
    return Array.from(this.registry.values());
  }
}

// Global registry
export const activityRegistry = new ActivityRegistry();

// Register activity types
activityRegistry.register('poll', 'Polling', PollingActivity);
activityRegistry.register('qna', 'Q&A', QnaActivity);
activityRegistry.register('word_cloud', 'Word Cloud', WordCloudActivity);
```

### Step 12: Polling Activity Components
**Files:** `frontend/src/components/activities/PollingActivity/`

```typescript
// frontend/src/components/activities/PollingActivity/index.ts
export { default as PollingActivity } from './PollingActivity';

// frontend/src/components/activities/PollingActivity/PollingActivity.tsx
import { BaseActivityComponent } from '../base/BaseActivity';
import PollingAdmin from './PollingAdmin';
import PollingViewer from './PollingViewer';
import PollingParticipant from './PollingParticipant';

export default class PollingActivity extends BaseActivityComponent {
  renderAdmin(props: AdminActivityProps) {
    return <PollingAdmin {...props} />;
  }
  
  renderViewer(props: ViewerActivityProps) {
    return <PollingViewer {...props} />;
  }
  
  renderParticipant(props: ParticipantActivityProps) {
    return <PollingParticipant {...props} />;
  }
}

// frontend/src/components/activities/PollingActivity/PollingAdmin.tsx
export default function PollingAdmin({
  activity,
  configuration,
  onConfigUpdate,
  onSave
}: AdminActivityProps) {
  const [question, setQuestion] = useState(configuration.question || '');
  const [options, setOptions] = useState(configuration.options || ['', '']);
  
  const handleSave = () => {
    onConfigUpdate({ question, options });
    onSave();
  };
  
  return (
    <div className="polling-admin">
      <h3>Configure Polling Activity</h3>
      <div className="form-group">
        <label>Question:</label>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your polling question"
        />
      </div>
      <div className="form-group">
        <label>Options:</label>
        {options.map((option, index) => (
          <input
            key={index}
            type="text"
            value={option}
            onChange={(e) => {
              const newOptions = [...options];
              newOptions[index] = e.target.value;
              setOptions(newOptions);
            }}
          />
        ))}
        <button onClick={() => setOptions([...options, ''])}>
          Add Option
        </button>
      </div>
      <button onClick={handleSave}>Save Configuration</button>
    </div>
  );
}

// frontend/src/components/activities/PollingActivity/PollingViewer.tsx  
export default function PollingViewer({
  activity,
  configuration,
  responses
}: ViewerActivityProps) {
  const results = useMemo(() => {
    // Process responses to calculate results
    const tallies = {};
    responses.forEach(response => {
      response.response_data.selected_options?.forEach(option => {
        tallies[option] = (tallies[option] || 0) + 1;
      });
    });
    return tallies;
  }, [responses]);
  
  return (
    <div className="polling-viewer">
      <h2>{configuration.question}</h2>
      <div className="results-chart">
        {Object.entries(results).map(([option, count]) => (
          <div key={option} className="result-bar">
            <span className="option-text">{option}</span>
            <div className="bar" style={{ width: `${(count / responses.length) * 100}%` }}>
              <span className="count">{count}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// frontend/src/components/activities/PollingActivity/PollingParticipant.tsx
export default function PollingParticipant({
  activity,
  configuration,
  onSubmitResponse,
  canSubmit,
  hasSubmitted
}: ParticipantActivityProps) {
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  
  const handleSubmit = () => {
    onSubmitResponse({ selected_options: selectedOptions });
  };
  
  return (
    <div className="polling-participant">
      <h3>{configuration.question}</h3>
      <div className="options">
        {configuration.options?.map((option, index) => (
          <label key={index} className="option">
            <input
              type={configuration.allow_multiple_choice ? "checkbox" : "radio"}
              name="poll-option"
              value={option}
              checked={selectedOptions.includes(option)}
              onChange={(e) => {
                if (configuration.allow_multiple_choice) {
                  setSelectedOptions(prev => 
                    e.target.checked 
                      ? [...prev, option]
                      : prev.filter(o => o !== option)
                  );
                } else {
                  setSelectedOptions([option]);
                }
              }}
            />
            {option}
          </label>
        ))}
      </div>
      <button 
        onClick={handleSubmit}
        disabled={!canSubmit || selectedOptions.length === 0}
      >
        {hasSubmitted ? 'Update Response' : 'Submit Response'}
      </button>
    </div>
  );
}
```

## Phase 5: Integration & Testing

### Step 13: Activity Renderer Component
**Files:** `frontend/src/components/ActivityRenderer.tsx`

```typescript
import { activityRegistry } from '@/lib/activityRegistry';
import { useActivityData } from '@/hooks/useActivityData';

interface ActivityRendererProps {
  activity: Activity;
  persona: 'admin' | 'viewer' | 'participant';
  onConfigUpdate?: (config: Record<string, unknown>) => void;
  onSubmitResponse?: (response: unknown) => void;
}

export default function ActivityRenderer({
  activity,
  persona,
  onConfigUpdate,
  onSubmitResponse
}: ActivityRendererProps) {
  const { responses, isLoading } = useActivityData(activity.id);
  const activityType = activityRegistry.get(activity.type);
  
  if (!activityType) {
    return <div>Unknown activity type: {activity.type}</div>;
  }
  
  const ActivityComponent = activityType.component;
  const instance = new ActivityComponent();
  
  const baseProps = {
    activity,
    configuration: activity.configuration,
    onStateChange: (newState) => {
      // Handle state changes via API
    }
  };
  
  switch (persona) {
    case 'admin':
      return instance.renderAdmin({
        ...baseProps,
        onConfigUpdate: onConfigUpdate!,
        onSave: () => {
          // Save activity configuration
        }
      });
      
    case 'viewer':
      return instance.renderViewer({
        ...baseProps,
        responses: responses || [],
        liveResults: true
      });
      
    case 'participant':
      return instance.renderParticipant({
        ...baseProps,
        onSubmitResponse: onSubmitResponse!,
        canSubmit: activity.state === 'active',
        hasSubmitted: false // Check if user has submitted
      });
      
    default:
      return <div>Invalid persona: {persona}</div>;
  }
}
```

### Step 14: Activity Management Integration
**Files:** `frontend/src/routes/admin/activities/`, update existing admin routes

```typescript
// Enhance existing admin activity management
import { ActivityRenderer } from '@/components/ActivityRenderer';
import { useActivityTypes } from '@/hooks/useActivityTypes';

export default function ActivityManagement() {
  const { data: activityTypes } = useActivityTypes();
  const [selectedType, setSelectedType] = useState<string>('');
  const [activities, setActivities] = useState<Activity[]>([]);
  
  return (
    <div className="activity-management">
      <div className="activity-type-selector">
        <h3>Create New Activity</h3>
        <select 
          value={selectedType} 
          onChange={(e) => setSelectedType(e.target.value)}
        >
          <option value="">Select Activity Type</option>
          {activityTypes?.map(type => (
            <option key={type.id} value={type.id}>{type.name}</option>
          ))}
        </select>
      </div>
      
      <div className="activity-list">
        <h3>Session Activities</h3>
        {activities.map(activity => (
          <div key={activity.id} className="activity-card">
            <h4>{activity.title}</h4>
            <ActivityRenderer 
              activity={activity}
              persona="admin"
              onConfigUpdate={(config) => {
                // Update activity configuration
              }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Step 15: Testing Implementation
**Files:** `backend/tests/test_activity_framework.py`, `frontend/src/__tests__/ActivityFramework.test.tsx`

```python
# backend/tests/test_activity_framework.py
import pytest
from app.services.activity_framework import ActivityRegistry, ActivityStateMachine
from app.services.activity_types.polling import PollingActivity

class TestActivityFramework:
    def test_activity_registry(self):
        """Test activity type registration."""
        ActivityRegistry.register('test', PollingActivity, PollingActivity.SCHEMA)
        assert 'test' in ActivityRegistry.get_all_types()
        
    def test_state_machine_transitions(self):
        """Test activity state transitions."""
        assert ActivityStateMachine.can_transition('draft', 'published')
        assert not ActivityStateMachine.can_transition('expired', 'active')
        
    def test_polling_activity_validation(self):
        """Test polling activity configuration validation."""
        activity = PollingActivity(None, {})
        
        valid_config = {
            'question': 'Test question?',
            'options': ['Option 1', 'Option 2']
        }
        assert activity.validate_config(valid_config)
        
        invalid_config = {'question': 'Test?'}  # Missing options
        assert not activity.validate_config(invalid_config)

# frontend/src/__tests__/ActivityFramework.test.tsx
import { render, screen } from '@testing-library/react';
import { ActivityRenderer } from '@/components/ActivityRenderer';
import { mockActivity } from './fixtures';

describe('ActivityFramework', () => {
  test('renders admin interface for polling activity', () => {
    render(
      <ActivityRenderer 
        activity={mockActivity}
        persona="admin"
        onConfigUpdate={jest.fn()}
      />
    );
    
    expect(screen.getByText('Configure Polling Activity')).toBeInTheDocument();
  });
  
  test('renders participant interface for polling activity', () => {
    render(
      <ActivityRenderer
        activity={mockActivity}
        persona="participant" 
        onSubmitResponse={jest.fn()}
      />
    );
    
    expect(screen.getByRole('button', { name: /submit response/i })).toBeInTheDocument();
  });
});
```

### Step 16: API Integration Updates
**Files:** `frontend/src/api/`, update generated API client usage

```typescript
// frontend/src/hooks/useActivityFramework.ts
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/api/generated';

export const useActivityTypes = () => {
  return useQuery({
    queryKey: ['activityTypes'],
    queryFn: () => api.activities.getActivityTypes()
  });
};

export const useActivityTransition = () => {
  return useMutation({
    mutationFn: ({ activityId, targetState, reason }: {
      activityId: string;
      targetState: string;
      reason?: string;
    }) => api.activities.transitionActivityState(activityId, { 
      target_state: targetState,
      reason 
    })
  });
};

export const useCreateActivity = () => {
  return useMutation({
    mutationFn: (activityData: CreateActivityRequest) => 
      api.activities.createActivity(activityData)
  });
};
```

### Step 17: Documentation and Final Integration
**Files:** `docs/ACTIVITY_FRAMEWORK.md`, update existing documentation

```markdown
# Activity Framework Documentation

## Adding New Activity Types

### Backend Implementation
1. Create activity class extending `BaseActivity`
2. Implement required methods: `validate_config`, `get_schema`, `process_response`
3. Register in `registration.py`

### Frontend Implementation  
1. Create activity directory: `frontend/src/components/activities/YourActivity/`
2. Implement three persona components: `Admin.tsx`, `Viewer.tsx`, `Participant.tsx`
3. Create main activity class extending `BaseActivityComponent`
4. Register in `activityRegistry.ts`

### Example: Simple Yes/No Activity
[Include complete code example showing all required files]

## Framework Architecture
[Document the complete architecture, patterns, and extensibility points]
```

## Validation & Acceptance Testing

### Framework Validation Checklist
- [ ] Activity types register successfully at startup
- [ ] State transitions work correctly for all activity types  
- [ ] Configuration validation prevents invalid activities
- [ ] All three persona interfaces render for each activity type
- [ ] API endpoints handle framework operations correctly
- [ ] Database schema supports extensible activity data
- [ ] Frontend registry loads activity types dynamically
- [ ] Error handling works for unknown activity types

### Performance Testing
- [ ] Framework loading time under 1 second
- [ ] Activity instantiation under 100ms
- [ ] State transitions complete under 200ms
- [ ] Configuration validation under 50ms
- [ ] Support 50+ concurrent participants per activity

### Integration Testing  
- [ ] Activities integrate with existing session management
- [ ] Participant responses save correctly
- [ ] Real-time polling updates activity states
- [ ] Admin controls work across all activity types
- [ ] Mobile participant interface works on iOS/Android

## Success Criteria

Upon completion:
1. ✅ **Extensible Foundation:** New activity types added by creating classes and registering
2. ✅ **Universal Personas:** All activities support admin/viewer/participant interfaces  
3. ✅ **Static Registration:** Activity types discovered at compile time with validation
4. ✅ **Type Safety:** Full TypeScript support for activity configurations and components
5. ✅ **State Management:** Robust state machine handling activity lifecycles
6. ✅ **Database Support:** Flexible schema supporting various activity configurations
7. ✅ **API Complete:** Full REST API for activity management and state transitions
8. ✅ **Frontend Framework:** Component architecture supporting easy activity addition
9. ✅ **Testing Coverage:** Comprehensive tests for framework and activity implementations
10. ✅ **Documentation:** Clear guides for adding new activity types

The framework provides a solid foundation for MVP while enabling rapid addition of new activity types as the platform grows.