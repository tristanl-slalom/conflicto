# Implementation Plan: Build Extensible Activity Framework

**GitHub Issue:** [#7](https://github.com/tristanl-slalom/conflicto/issues/7)
**Generated:** 2025-10-08T13:38:22Z
**Labels:** feature:activity-framework, priority:critical, phase:mvp
**Assignee:** josephc-slalom

## Implementation Strategy

This implementation follows a bottom-up approach, building core framework components first, then implementing concrete activity types, and finally creating the multi-persona UI components. The strategy ensures a solid foundation while maintaining simplicity and ease of adding new activity types.

### Key Principles
1. **Framework First:** Build extensible base classes and interfaces
2. **Type Safety:** Leverage TypeScript for compile-time validation
3. **Static Registration:** Simple registry pattern for activity types
4. **Multi-Persona Support:** Consistent experience across admin/viewer/participant
5. **Test-Driven:** Comprehensive test coverage for framework reliability

## File Structure Changes

### New Backend Files
```
backend/app/
├── db/
│   ├── models.py                     # Add Activity, ActivityResponse models
│   └── enums.py                      # Add ActivityState enum
├── models/
│   ├── schemas.py                    # Add activity-related Pydantic schemas
│   └── jsonb_schemas/
│       ├── activity_base.json        # Base activity configuration schema
│       ├── activity_metadata.json    # Activity metadata schema
│       └── plugins/                  # Plugin-specific schemas
│           ├── polling.json
│           ├── qna.json
│           └── wordcloud.json
├── services/
│   ├── activity_service.py           # Core activity business logic
│   ├── activity_type_service.py      # Activity type registry and management
│   └── activity_state_machine.py     # Activity lifecycle state management
├── routes/
│   ├── activities.py                 # Activity CRUD endpoints
│   └── activity_types.py             # Activity type registry endpoints
├── core/
│   ├── activity_framework/
│   │   ├── __init__.py
│   │   ├── base_activity.py          # Abstract base activity class
│   │   ├── activity_registry.py      # Activity type registry
│   │   ├── schema_validator.py       # JSON schema validation utilities
│   │   └── state_machine.py          # Activity state transition logic
│   └── exceptions.py                 # Add activity-specific exceptions
└── activities/
    ├── __init__.py
    ├── base_activity.py              # Abstract activity interface
    ├── polling_activity.py           # Polling activity implementation
    ├── qna_activity.py               # Q&A activity implementation
    └── wordcloud_activity.py         # Word cloud activity implementation
```

### New Frontend Files
```
frontend/src/
├── types/
│   ├── activity.ts                   # Activity type definitions
│   └── plugins.ts                    # Plugin interface definitions
├── api/
│   ├── activities.ts                 # Activity API client functions
│   └── activity-types.ts             # Activity type API client functions
├── hooks/
│   ├── useActivities.ts              # Activity data management hooks
│   ├── useActivityState.ts           # Activity state management hooks
│   └── useActivityTypes.ts           # Activity type registry hooks
├── components/
│   ├── activities/
│   │   ├── ActivityFramework/
│   │   │   ├── index.ts
│   │   │   ├── BaseActivity.tsx      # Base activity component
│   │   │   ├── AdminActivityWrapper.tsx    # Admin persona wrapper
│   │   │   ├── ViewerActivityWrapper.tsx   # Viewer persona wrapper
│   │   │   ├── ParticipantActivityWrapper.tsx # Participant persona wrapper
│   │   │   └── ActivityStateIndicator.tsx  # State visualization
│   │   ├── ActivityList/
│   │   │   ├── index.ts
│   │   │   ├── ActivityList.tsx      # Activity management list
│   │   │   └── ActivityCard.tsx      # Individual activity card
│   │   ├── ActivityConfiguration/
│   │   │   ├── index.ts
│   │   │   ├── ActivityConfigForm.tsx # Dynamic config form
│   │   │   ├── SchemaFormBuilder.tsx # JSON schema to form converter
│   │   │   └── ConfigPreview.tsx     # Configuration preview
│   │   ├── PollingActivity/
│   │   │   ├── index.ts
│   │   │   ├── PollingAdmin.tsx      # Admin polling configuration
│   │   │   ├── PollingViewer.tsx     # Viewer polling display
│   │   │   └── PollingParticipant.tsx # Participant voting interface
│   │   ├── QnaActivity/
│   │   │   ├── index.ts
│   │   │   ├── QnaAdmin.tsx          # Admin Q&A management
│   │   │   ├── QnaViewer.tsx         # Viewer Q&A display
│   │   │   └── QnaParticipant.tsx    # Participant question interface
│   │   └── WordCloudActivity/
│   │       ├── index.ts
│   │       ├── WordCloudAdmin.tsx    # Admin word cloud config
│   │       ├── WordCloudViewer.tsx   # Viewer word cloud display
│   │       └── WordCloudParticipant.tsx # Participant word input
│   └── common/
│       ├── LoadingStates/
│       │   └── ActivityLoading.tsx   # Activity-specific loading states
│       └── ErrorBoundaries/
│           └── ActivityErrorBoundary.tsx # Activity error handling
├── lib/
│   ├── activity-framework/
│   │   ├── plugin-loader.ts          # Dynamic plugin component loading
│   │   ├── schema-validator.ts       # Client-side schema validation
│   │   └── state-manager.ts          # Activity state synchronization
│   └── validation/
│       └── activity-schemas.ts       # Shared validation schemas
└── routes/
    ├── activities/
    │   ├── index.tsx                 # Activity management page
    │   ├── create.tsx                # Activity creation page
    │   └── $activityId.tsx           # Individual activity page
    └── session/
        └── $sessionId/
            └── activities.tsx        # Session activity management
```

### Database Migration Files
```
backend/migrations/versions/
├── 001_add_activity_tables.py       # Create activities and related tables
├── 002_add_activity_indexes.py      # Add performance indexes
└── 003_add_activity_constraints.py  # Add data integrity constraints
```

### Modified Files
```
backend/app/
├── db/models.py                      # Add session.activities relationship
├── main.py                           # Register activity routes
└── routes/__init__.py                # Export activity routes

frontend/src/
├── routes/session/$sessionId.tsx     # Add activity management section
├── components/sessions/SessionDetail.tsx # Integrate activity management
└── api/index.ts                      # Export activity API functions
```

## Implementation Steps

### Phase 1: Backend Framework Foundation (Steps 1-4)

#### Step 1: Database Schema and Models
**Files:** `backend/migrations/versions/001_add_activity_tables.py`, `backend/app/db/models.py`, `backend/app/db/enums.py`

1. **Create Alembic Migration**
   - Generate migration for activities and activity_responses tables
   - Add ActivityState enum type
   - Create indexes for performance optimization

2. **Implement SQLAlchemy Models**
   - Add Activity model with JSONB configuration and metadata fields
   - Add ActivityResponse model for storing user responses
   - Update Session model to include activities relationship

3. **Add Database Enums**
   - Define ActivityState enum (draft, published, active, expired)
   - Add validation constraints for state transitions

#### Step 2: Core Activity Framework
**Files:** `backend/app/core/activity_framework/`, `backend/app/models/schemas.py`

1. **Abstract Base Activity Class**
   ```python
   # backend/app/core/activity_framework/base_activity.py
   from abc import ABC, abstractmethod
   from typing import Dict, Any, Optional
   
   class BaseActivity(ABC):
       @abstractmethod
       async def validate_configuration(self, config: Dict[str, Any]) -> bool:
           """Validate activity-specific configuration"""
           pass
           
       @abstractmethod
       async def initialize_activity(self, activity_id: str) -> None:
           """Initialize activity with default state"""
           pass
           
       @abstractmethod  
       async def process_response(self, activity_id: str, response_data: Dict[str, Any]) -> bool:
           """Process and validate participant response"""
           pass
   ```

2. **State Machine Implementation**
   ```python
   # backend/app/core/activity_framework/state_machine.py
   from enum import Enum
   from typing import Dict, Set, Optional
   
   class ActivityStateMachine:
       TRANSITIONS: Dict[ActivityState, Set[ActivityState]] = {
           ActivityState.DRAFT: {ActivityState.PUBLISHED},
           ActivityState.PUBLISHED: {ActivityState.ACTIVE, ActivityState.DRAFT},
           ActivityState.ACTIVE: {ActivityState.EXPIRED},
           ActivityState.EXPIRED: set()
       }
   ```

3. **Plugin Registry System**
   ```python
   # backend/app/core/activity_framework/plugin_registry.py
   class ActivityPluginRegistry:
       def __init__(self):
           self._plugins: Dict[str, BaseActivity] = {}
           
       def register_plugin(self, activity_type: str, plugin: BaseActivity):
           """Register an activity plugin"""
           
       def get_plugin(self, activity_type: str) -> Optional[BaseActivity]:
           """Get registered plugin by type"""
           
       def list_plugins(self) -> Dict[str, ActivityPlugin]:
           """List all registered plugins with metadata"""
   ```

4. **Pydantic Schemas**
   - ActivityCreate, ActivityUpdate, ActivityResponse schemas
   - ActivityWithState, ActivityPlugin schemas
   - Nested schemas for configuration and metadata validation

#### Step 3: Activity Services
**Files:** `backend/app/services/activity_service.py`, `backend/app/services/activity_plugin_service.py`, `backend/app/services/activity_state_machine.py`

1. **Activity Service Implementation**
   ```python
   class ActivityService:
       async def create_activity(self, session_id: str, activity_data: ActivityCreate) -> Activity:
           """Create new activity with validation"""
           
       async def update_activity_configuration(self, activity_id: str, config: dict) -> Activity:
           """Update activity configuration with schema validation"""
           
       async def transition_activity_state(self, activity_id: str, target_state: ActivityState, reason: str = None) -> Activity:
           """Safely transition activity state"""
           
       async def submit_response(self, activity_id: str, response_data: dict, user_context: dict) -> ActivityResponse:
           """Submit and validate participant response"""
   ```

2. **Plugin Service Implementation**
   ```python
   class ActivityTypeService:
       async def list_activity_types(self) -> List[ActivityType]:
           """List available activity types from registry"""
           
       async def create_activity(self, activity_type: str) -> BaseActivity:
           """Create and instantiate activity from type"""
           
       async def validate_activity_configuration(self, activity_type: str, config: dict) -> ValidationResult:
           """Validate configuration against activity type schema"""
   ```

3. **State Machine Service**
   ```python
   class ActivityStateMachineService:
       async def can_transition(self, current_state: ActivityState, target_state: ActivityState) -> bool:
           """Check if state transition is valid"""
           
       async def execute_transition(self, activity_id: str, target_state: ActivityState, reason: str = None) -> Activity:
           """Execute state transition and update activity"""
   ```

#### Step 4: API Routes
**Files:** `backend/app/routes/activities.py`, `backend/app/routes/activity_plugins.py`, `backend/app/main.py`

1. **Activity CRUD Routes**
   ```python
   @router.post("/sessions/{session_id}/activities")
   async def create_activity(session_id: str, activity_data: ActivityCreate) -> Activity:
       """Create new activity in session"""
       
   @router.get("/activities/{activity_id}")
   async def get_activity(activity_id: str) -> ActivityWithState:
       """Get activity with current state and metadata"""
       
   @router.put("/activities/{activity_id}")  
   async def update_activity(activity_id: str, activity_data: ActivityUpdate) -> Activity:
       """Update activity configuration"""
       
   @router.post("/activities/{activity_id}/transition")
   async def transition_activity_state(activity_id: str, transition_data: StateTransition) -> Activity:
       """Transition activity to new state"""
   ```

2. **Response Management Routes**
   ```python
   @router.post("/activities/{activity_id}/responses")
   async def submit_response(activity_id: str, response_data: dict) -> ActivityResponse:
       """Submit participant response"""
       
   @router.get("/activities/{activity_id}/responses")
   async def get_activity_responses(activity_id: str) -> List[ActivityResponse]:
       """Get all responses for activity (admin only)"""
   ```

3. **Activity Type Registry Routes**
   ```python
   @router.get("/activities/types")
   async def list_activity_types() -> List[ActivityType]:
       """List available activity types from static registry"""
       
   @router.get("/activities/types/{type_id}/schema")
   async def get_activity_type_schema(type_id: str) -> JSONSchema:
       """Get configuration schema for activity type"""
   ```

### Phase 2: Built-in Activity Types (Steps 5-7)

#### Step 5: Activity Base Classes and JSON Schemas
**Files:** `backend/app/activities/base_activity.py`, `backend/app/models/jsonb_schemas/`

1. **Abstract Activity Interface**
   ```python
   # backend/app/activities/base_activity.py
   class BaseActivityType(BaseActivity):
       @property
       @abstractmethod
       def activity_type_id(self) -> str:
           """Unique activity type identifier"""
           
       @property
       @abstractmethod
       def schema(self) -> Dict[str, Any]:
           """JSON schema for configuration validation"""
           
       @classmethod
       @abstractmethod
       def get_metadata(cls) -> ActivityType:
           """Get activity type metadata"""
   ```

2. **JSON Schema Definitions**
   ```json
   // backend/app/models/jsonb_schemas/activity_base.json
   {
     "$schema": "http://json-schema.org/draft-07/schema#",
     "type": "object",
     "properties": {
       "title": {"type": "string", "maxLength": 500},
       "description": {"type": "string"},
       "duration_seconds": {"type": "integer", "minimum": 30},
       "max_responses": {"type": "integer", "minimum": 1},
       "allow_multiple_responses": {"type": "boolean"}
     },
     "required": ["title"]
   }
   ```

   ```json
   // backend/app/models/jsonb_schemas/activity_types/polling.json
   {
     "allOf": [{"$ref": "../activity_base.json"}],
     "properties": {
       "options": {
         "type": "array",
         "items": {"type": "string"},
         "minItems": 2,
         "maxItems": 10
       },
       "allow_multiple_choices": {"type": "boolean"},
       "show_live_results": {"type": "boolean"}
     },
     "required": ["options"]
   }
   ```

#### Step 6: Built-in Activity Type Implementations
**Files:** `backend/app/activities/`

1. **Polling Activity Implementation**
   ```python
   # backend/app/activities/polling_activity.py
   class PollingActivity(BaseActivityType):
       @property
       def activity_type_id(self) -> str:
           return "polling"
           
       async def validate_configuration(self, config: Dict[str, Any]) -> bool:
           """Validate polling-specific configuration"""
           schema = load_schema("activity_types/polling.json")
           return validate_json_schema(config, schema)
           
       async def process_response(self, activity_id: str, response_data: Dict[str, Any]) -> bool:
           """Process polling vote response"""
           # Validate response contains valid option selection
           # Check for duplicate responses if not allowed
   ```

2. **Q&A Activity Plugin**
   ```python
   # backend/app/plugins/builtin/qna_activity.py
   class QnaActivityPlugin(ActivityPlugin):
       @property
       def plugin_id(self) -> str:
           return "qna"
           
       async def process_response(self, activity_id: str, response_data: Dict[str, Any]) -> bool:
           """Process Q&A question submission"""
           # Validate question content
           # Check for spam/inappropriate content
           # Store question with upvote capability
   ```

3. **Word Cloud Activity Plugin**
   ```python
   # backend/app/plugins/builtin/wordcloud_activity.py
   class WordCloudActivityPlugin(ActivityPlugin):
       @property
       def plugin_id(self) -> str:
           return "wordcloud"
           
       async def process_response(self, activity_id: str, response_data: Dict[str, Any]) -> bool:
           """Process word cloud word submission"""
           # Validate word/phrase content
           # Check word length and content appropriateness
           # Aggregate word frequency for cloud generation
   ```

#### Step 7: Activity Type Registration
**Files:** `backend/app/core/activity_framework/activity_registry.py`, `backend/app/main.py`

1. **Static Registration Implementation**
   ```python
   def register_builtin_activity_types():
       """Register built-in activity types at startup"""
       from app.activities.builtin import PollingActivity, QnaActivity, WordCloudActivity
       
       registry = ActivityTypeRegistry()
       registry.register_type("polling", PollingActivity)
       registry.register_type("qna", QnaActivity) 
       registry.register_type("wordcloud", WordCloudActivity)
       return registry
   ```

2. **Application Startup Integration**
   ```python
   # backend/app/main.py
   @app.on_event("startup")
   async def startup_event():
       """Initialize application with static activity type registration"""
       activity_registry = register_builtin_activity_types()
       app.state.activity_registry = activity_registry
   ```

### Phase 3: Frontend Framework (Steps 8-11)

#### Step 8: TypeScript Interfaces and API Integration
**Files:** `frontend/src/types/`, `frontend/src/api/`

1. **Activity Type Definitions**
   ```typescript
   // frontend/src/types/activity.ts
   export interface Activity {
     id: string;
     session_id: string;
     type: string;
     title: string;
     description?: string;
     state: ActivityState;
     configuration: Record<string, unknown>;
     metadata: ActivityMetadata;
     created_at: string;
     updated_at: string;
     expires_at?: string;
   }
   
   export type ActivityState = 'draft' | 'published' | 'active' | 'expired';
   
   export interface ActivityPlugin {
     id: string;
     name: string;
     version: string;
     description: string;
     schema: JSONSchema;
     component_paths: {
       admin: string;
       viewer: string;
       participant: string;
     };
   }
   ```

2. **API Client Functions**
   ```typescript
   // frontend/src/api/activities.ts
   export const activitiesApi = {
     async createActivity(sessionId: string, data: CreateActivityRequest): Promise<Activity> {
       return apiClient.post(`/sessions/${sessionId}/activities`, data);
     },
     
     async getActivity(activityId: string): Promise<ActivityWithState> {
       return apiClient.get(`/activities/${activityId}`);
     },
     
     async updateConfiguration(activityId: string, config: Record<string, unknown>): Promise<Activity> {
       return apiClient.put(`/activities/${activityId}`, { configuration: config });
     },
     
     async transitionState(activityId: string, targetState: ActivityState, reason?: string): Promise<Activity> {
       return apiClient.post(`/activities/${activityId}/transition`, { target_state: targetState, reason });
     },
     
     async submitResponse(activityId: string, responseData: Record<string, unknown>): Promise<ActivityResponse> {
       return apiClient.post(`/activities/${activityId}/responses`, responseData);
     }
   };
   ```

#### Step 9: React Hooks for Activity Management
**Files:** `frontend/src/hooks/`

1. **Activity Data Hooks**
   ```typescript
   // frontend/src/hooks/useActivities.ts
   export function useActivities(sessionId: string) {
     return useQuery({
       queryKey: ['activities', sessionId],
       queryFn: () => activitiesApi.getSessionActivities(sessionId),
       refetchInterval: 3000, // 3-second polling
     });
   }
   
   export function useActivity(activityId: string) {
     return useQuery({
       queryKey: ['activity', activityId],
       queryFn: () => activitiesApi.getActivity(activityId),
       refetchInterval: 2000, // 2-second polling for active activities
     });
   }
   ```

2. **Activity State Management Hooks**
   ```typescript
   // frontend/src/hooks/useActivityState.ts
   export function useActivityStateTransition(activityId: string) {
     const queryClient = useQueryClient();
     
     return useMutation({
       mutationFn: ({ targetState, reason }: { targetState: ActivityState; reason?: string }) =>
         activitiesApi.transitionState(activityId, targetState, reason),
       onSuccess: () => {
         queryClient.invalidateQueries(['activity', activityId]);
         queryClient.invalidateQueries(['activities']);
       },
     });
   }
   ```

3. **Activity Type Registry Hooks**
   ```typescript
   // frontend/src/hooks/useActivityTypes.ts
   export function useActivityTypes() {
     return useQuery({
       queryKey: ['activity-types'],
       queryFn: () => activityTypesApi.listTypes(),
       staleTime: 5 * 60 * 1000, // 5 minutes
     });
   }
   ```

#### Step 10: Base Activity Components and Framework
**Files:** `frontend/src/components/activities/ActivityFramework/`

1. **Base Activity Component**
   ```typescript
   // frontend/src/components/activities/ActivityFramework/BaseActivity.tsx
   export interface BaseActivityProps<TConfig = Record<string, unknown>> {
     activity: Activity;
     configuration: TConfig;
     persona: 'admin' | 'viewer' | 'participant';
     onStateChange?: (newState: ActivityState) => void;
   }
   
   export function BaseActivity<TConfig = Record<string, unknown>>({
     activity,
     configuration,
     persona,
     children,
   }: PropsWithChildren<BaseActivityProps<TConfig>>) {
     return (
       <div className="activity-container" data-activity-type={activity.type} data-persona={persona}>
         <ActivityStateIndicator state={activity.state} />
         {children}
       </div>
     );
   }
   ```

2. **Persona-Specific Wrappers**
   ```typescript
   // frontend/src/components/activities/ActivityFramework/AdminActivityWrapper.tsx
   export function AdminActivityWrapper<TConfig = Record<string, unknown>>({
     activity,
     children,
     onConfigUpdate,
     onStateTransition,
   }: AdminActivityWrapperProps<TConfig>) {
     const { mutate: updateConfig } = useActivityConfigUpdate(activity.id);
     const { mutate: transitionState } = useActivityStateTransition(activity.id);
     
     return (
       <BaseActivity activity={activity} persona="admin">
         <div className="admin-controls">
           <ActivityStateControls
             currentState={activity.state}
             onTransition={transitionState}
           />
         </div>
         {children}
       </BaseActivity>
     );
   }
   ```

3. **Dynamic Component Loading**
   ```typescript
   // frontend/src/lib/activity-framework/plugin-loader.ts
   export class ActivityPluginLoader {
     private componentCache = new Map<string, React.ComponentType<any>>();
     
     async loadComponent(pluginId: string, persona: 'admin' | 'viewer' | 'participant'): Promise<React.ComponentType<any>> {
       const cacheKey = `${pluginId}-${persona}`;
       
       if (this.componentCache.has(cacheKey)) {
         return this.componentCache.get(cacheKey)!;
       }
       
       // Dynamic import based on activity type configuration
       const component = await import(`../components/activities/${activityType}/${activityType}${persona.charAt(0).toUpperCase() + persona.slice(1)}.tsx`);
       this.componentCache.set(cacheKey, component.default);
       return component.default;
     }
   }
   ```

#### Step 11: Activity Configuration Components
**Files:** `frontend/src/components/activities/ActivityConfiguration/`

1. **Dynamic Configuration Form**
   ```typescript
   // frontend/src/components/activities/ActivityConfiguration/ActivityConfigForm.tsx
   export function ActivityConfigForm({
     plugin,
     initialConfig,
     onConfigChange,
     onSave,
   }: ActivityConfigFormProps) {
     const { data: schema } = useQuery({
       queryKey: ['plugin-schema', plugin.id],
       queryFn: () => pluginsApi.getPluginSchema(plugin.id),
     });
     
     return (
       <div className="activity-config-form">
         <SchemaFormBuilder
           schema={schema}
           initialValues={initialConfig}
           onChange={onConfigChange}
         />
         <ConfigPreview config={currentConfig} plugin={plugin} />
       </div>
     );
   }
   ```

2. **JSON Schema Form Builder**
   ```typescript
   // frontend/src/components/activities/ActivityConfiguration/SchemaFormBuilder.tsx
   export function SchemaFormBuilder({
     schema,
     initialValues,
     onChange,
   }: SchemaFormBuilderProps) {
     // Convert JSON schema to form fields
     // Support various input types: text, number, select, checkbox, array
     // Implement validation based on schema constraints
     
     return (
       <Form>
         {renderFieldsFromSchema(schema, initialValues, onChange)}
       </Form>
     );
   }
   ```

### Phase 4: Built-in Activity UI Components (Steps 12-14)

#### Step 12: Polling Activity Components
**Files:** `frontend/src/components/activities/PollingActivity/`

1. **Admin Polling Configuration**
   ```typescript
   // PollingAdmin.tsx
   export function PollingAdmin({ activity, onConfigUpdate }: PollingAdminProps) {
     const [options, setOptions] = useState<string[]>(activity.configuration.options || ['']);
     
     return (
       <AdminActivityWrapper activity={activity} onConfigUpdate={onConfigUpdate}>
         <div className="polling-config">
           <h3>Poll Configuration</h3>
           <OptionsEditor options={options} onChange={setOptions} />
           <SettingsPanel
             allowMultipleChoices={activity.configuration.allow_multiple_choices}
             showLiveResults={activity.configuration.show_live_results}
           />
         </div>
       </AdminActivityWrapper>
     );
   }
   ```

2. **Viewer Polling Display**
   ```typescript
   // PollingViewer.tsx
   export function PollingViewer({ activity }: PollingViewerProps) {
     const { data: responses } = useActivityResponses(activity.id);
     const results = useMemo(() => calculateResults(responses), [responses]);
     
     return (
       <ViewerActivityWrapper activity={activity}>
         <div className="polling-display">
           <h2>{activity.title}</h2>
           <ResultsChart results={results} showLive={activity.configuration.show_live_results} />
           <QRCodeForParticipants activityId={activity.id} />
         </div>
       </ViewerActivityWrapper>
     );
   }
   ```

3. **Participant Polling Interface**
   ```typescript
   // PollingParticipant.tsx
   export function PollingParticipant({ activity, onSubmitResponse }: PollingParticipantProps) {
     const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
     const { mutate: submitVote } = useSubmitResponse(activity.id);
     
     return (
       <ParticipantActivityWrapper activity={activity}>
         <div className="polling-participate">
           <h2>{activity.title}</h2>
           <OptionsList
             options={activity.configuration.options}
             selected={selectedOptions}
             onChange={setSelectedOptions}
             multipleChoice={activity.configuration.allow_multiple_choices}
           />
           <SubmitButton onClick={() => submitVote({ selected_options: selectedOptions })} />
         </div>
       </ParticipantActivityWrapper>
     );
   }
   ```

#### Step 13: Q&A Activity Components
**Files:** `frontend/src/components/activities/QnaActivity/`

1. **Admin Q&A Management**
   ```typescript
   // QnaAdmin.tsx
   export function QnaAdmin({ activity }: QnaAdminProps) {
     const { data: questions } = useActivityResponses(activity.id);
     
     return (
       <AdminActivityWrapper activity={activity}>
         <div className="qna-admin">
           <QuestionModerationPanel questions={questions} />
           <LiveQuestionsDisplay questions={questions.filter(q => q.approved)} />
         </div>
       </AdminActivityWrapper>
     );
   }
   ```

2. **Viewer Q&A Display**
   ```typescript
   // QnaViewer.tsx
   export function QnaViewer({ activity }: QnaViewerProps) {
     const { data: approvedQuestions } = useApprovedQuestions(activity.id);
     
     return (
       <ViewerActivityWrapper activity={activity}>
         <div className="qna-display">
           <h2>{activity.title}</h2>
           <QuestionsQueue questions={approvedQuestions} />
           <QRCodeForParticipants activityId={activity.id} />
         </div>
       </ViewerActivityWrapper>
     );
   }
   ```

3. **Participant Question Interface**
   ```typescript
   // QnaParticipant.tsx
   export function QnaParticipant({ activity }: QnaParticipantProps) {
     const [question, setQuestion] = useState('');
     const { mutate: submitQuestion } = useSubmitResponse(activity.id);
     
     return (
       <ParticipantActivityWrapper activity={activity}>
         <div className="qna-participate">
           <h2>{activity.title}</h2>
           <QuestionInput
             value={question}
             onChange={setQuestion}
             placeholder="Ask your question..."
           />
           <SubmitButton onClick={() => submitQuestion({ question })} />
           <MyQuestionsHistory activityId={activity.id} />
         </div>
       </ParticipantActivityWrapper>
     );
   }
   ```

#### Step 14: Word Cloud Activity Components
**Files:** `frontend/src/components/activities/WordCloudActivity/`

1. **Admin Word Cloud Configuration**
   ```typescript
   // WordCloudAdmin.tsx
   export function WordCloudAdmin({ activity }: WordCloudAdminProps) {
     const { data: words } = useActivityResponses(activity.id);
     const wordFrequency = useMemo(() => calculateWordFrequency(words), [words]);
     
     return (
       <AdminActivityWrapper activity={activity}>
         <div className="wordcloud-admin">
           <WordCloudPreview words={wordFrequency} />
           <WordModerationPanel words={words} />
         </div>
       </AdminActivityWrapper>
     );
   }
   ```

2. **Viewer Word Cloud Display**
   ```typescript
   // WordCloudViewer.tsx
   export function WordCloudViewer({ activity }: WordCloudViewerProps) {
     const { data: words } = useApprovedWords(activity.id);
     const wordFrequency = useMemo(() => calculateWordFrequency(words), [words]);
     
     return (
       <ViewerActivityWrapper activity={activity}>
         <div className="wordcloud-display">
           <h2>{activity.title}</h2>
           <WordCloudVisualization words={wordFrequency} />
           <QRCodeForParticipants activityId={activity.id} />
         </div>
       </ViewerActivityWrapper>
     );
   }
   ```

3. **Participant Word Input Interface**
   ```typescript
   // WordCloudParticipant.tsx
   export function WordCloudParticipant({ activity }: WordCloudParticipantProps) {
     const [words, setWords] = useState<string[]>(['']);
     const { mutate: submitWords } = useSubmitResponse(activity.id);
     
     return (
       <ParticipantActivityWrapper activity={activity}>
         <div className="wordcloud-participate">
           <h2>{activity.title}</h2>
           <WordInput
             words={words}
             onChange={setWords}
             maxWords={activity.configuration.max_words_per_user || 3}
           />
           <SubmitButton onClick={() => submitWords({ words: words.filter(w => w.trim()) })} />
         </div>
       </ParticipantActivityWrapper>
     );
   }
   ```

### Phase 5: Integration and Testing (Steps 15-17)

#### Step 15: Session Integration
**Files:** `frontend/src/routes/session/$sessionId.tsx`, `frontend/src/components/sessions/`

1. **Session Activity Management**
   ```typescript
   // frontend/src/routes/session/$sessionId/activities.tsx
   export function SessionActivities() {
     const { sessionId } = useParams();
     const { data: activities } = useActivities(sessionId);
     const { data: plugins } = useActivityPlugins();
     
     return (
       <div className="session-activities">
         <ActivityList activities={activities} />
         <CreateActivityButton plugins={plugins} sessionId={sessionId} />
       </div>
     );
   }
   ```

2. **Activity Management Integration**
   ```typescript
   // Update frontend/src/components/sessions/SessionDetail.tsx
   export function SessionDetail({ session }: SessionDetailProps) {
     return (
       <div className="session-detail">
         <SessionInfo session={session} />
         <Tabs>
           <Tab label="Overview">
             <SessionOverview session={session} />
           </Tab>
           <Tab label="Activities">
             <SessionActivities sessionId={session.id} />
           </Tab>
           <Tab label="Participants">
             <SessionParticipants sessionId={session.id} />
           </Tab>
         </Tabs>
       </div>
     );
   }
   ```

#### Step 16: Comprehensive Testing Suite
**Files:** `backend/tests/`, `frontend/src/__tests__/`

1. **Backend Unit Tests**
   ```python
   # backend/tests/test_activity_framework.py
   class TestActivityFramework:
       async def test_activity_creation(self):
           """Test activity creation with valid configuration"""
           
       async def test_state_transitions(self):
           """Test valid and invalid state transitions"""
           
       async def test_activity_type_registration(self):
           """Test static activity type registration"""
           
       async def test_configuration_validation(self):
           """Test JSON schema validation for activity configs"""
   ```

2. **Frontend Component Tests**
   ```typescript
   // frontend/src/__tests__/components/ActivityFramework.test.tsx
   describe('Activity Framework Components', () => {
     test('renders activity with correct persona wrapper', () => {
       // Test persona-specific rendering
     });
     
     test('handles configuration updates correctly', () => {
       // Test config form functionality
     });
     
     test('manages activity state transitions', () => {
       // Test state transition UI
     });
   });
   ```

3. **Integration Tests**
   ```python
   # backend/tests/test_activity_integration.py
   class TestActivityIntegration:
       async def test_end_to_end_polling_flow(self):
           """Test complete polling activity lifecycle"""
           
       async def test_multi_user_activity_responses(self):
           """Test concurrent user responses to activities"""
           
       async def test_activity_expiration_handling(self):
           """Test automatic activity expiration"""
   ```

#### Step 17: Documentation and API Updates
**Files:** `backend/openapi.json`, `frontend/docs/`, `docs/`

1. **OpenAPI Documentation Updates**
   - Update `backend/openapi.json` with activity endpoints
   - Document request/response schemas for all activity operations
   - Include examples for each activity type configuration

2. **Component Documentation**
   ```markdown
   # frontend/docs/components.md
   ## Activity Framework Components
   
   ### BaseActivity
   Base component for all activity types with persona support.
   
   ### ActivityConfigForm
   Dynamic form generation from JSON schemas for activity configuration.
   
   ### Plugin System
   How to create new activity plugins and register them.
   ```

3. **Architecture Documentation**
   ```markdown
   # docs/ACTIVITY_FRAMEWORK.md
   ## Activity Framework Architecture
   
   ### Overview
   The activity framework provides extensible support for different types of interactive activities.
   
   ### Plugin Development
   Step-by-step guide for creating new activity plugins.
   
   ### State Management
   Activity lifecycle and state transition rules.
   ```

## Testing Strategy

### Unit Testing Coverage
- **Backend Services:** 90%+ coverage for activity service, plugin service, state machine
- **Frontend Components:** 85%+ coverage for framework components and plugin components
- **Schema Validation:** 100% coverage for configuration validation logic
- **State Machine:** 100% coverage for state transition logic

### Integration Testing
- **API Integration:** End-to-end testing for all activity endpoints
- **Database Integration:** Testing with real database for complex queries
- **Activity Type Registry:** Testing static type registration and lookup
- **Multi-Persona Flow:** Testing activity workflow across all personas

### Performance Testing
- **Concurrent Users:** Test 50+ concurrent participants per activity
- **Response Times:** API responses under 200ms for activity operations
- **Memory Usage:** Monitor memory consumption with multiple active activities
- **Database Performance:** Optimize queries for activity and response data

## Deployment Considerations

### Database Migrations
- **Schema Migration:** Deploy activity tables and constraints
- **Index Creation:** Add performance indexes for activity queries
- **Data Migration:** No existing data migration needed (new feature)

### Environment Variables
```bash
# Add to backend environment
ACTIVITY_STATE_TIMEOUT_SECONDS=3600
ACTIVITY_MAX_RESPONSES_PER_USER=10
```

### Configuration Changes
- **Activity Registry:** Static activity type registration at startup
- **Caching:** Redis caching for activity state and response data

## Risk Assessment

### Technical Risks
- **Component Loading Performance:** Mitigate with React lazy loading and code splitting
- **State Concurrency:** Use database transactions and optimistic locking
- **TypeScript Compilation:** Ensure compile-time type validation works correctly
- **Memory Usage:** Monitor activity instance lifecycle and cleanup

### Integration Risks  
- **Session Integration:** Ensure backwards compatibility with existing session management
- **Authentication:** Properly scope activity access to session participants
- **Real-time Updates:** Polling interval optimization for performance vs responsiveness

### Mitigation Strategies
- **Gradual Rollout:** Deploy framework first, then add activity types incrementally
- **Feature Flags:** Use feature flags to control activity type availability
- **Monitoring:** Comprehensive monitoring for activity performance and errors
- **Rollback Plan:** Ability to disable activity framework without system impact

## Estimated Effort

### Development Timeline (5-7 days)
- **Phase 1 (Backend Framework):** 2 days
- **Phase 2 (Built-in Plugins):** 1 day  
- **Phase 3 (Frontend Framework):** 2 days
- **Phase 4 (Plugin UI Components):** 1.5 days
- **Phase 5 (Integration & Testing):** 0.5 days

### Complexity Assessment
- **High Complexity:** Plugin architecture and dynamic component loading
- **Medium Complexity:** State machine implementation and multi-persona UI
- **Low Complexity:** Basic CRUD operations and schema validation

### Resource Requirements
- **Backend Developer:** 3 days (framework, plugins, API)
- **Frontend Developer:** 3 days (components, integration, UI)
- **Full-Stack Integration:** 1 day (testing, deployment, documentation)

This implementation plan provides a comprehensive roadmap for building the extensible activity framework while maintaining code quality, test coverage, and architectural consistency with the existing Caja platform.