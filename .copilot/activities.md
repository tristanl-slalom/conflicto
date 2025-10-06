# Activity Framework Implementation

## Activity Framework Overview

The Caja platform uses a modular activity framework that allows for easy addition of new activity types while maintaining consistent behavior across all activities.

## Core Activity Architecture

### Activity Base Interface
Every activity type must implement the following core interface:

```typescript
interface BaseActivity {
  id: UUID;
  type: ActivityType;
  title: string;
  description?: string;
  config: ActivityConfig;
  status: ActivityStatus;
  timeout_seconds?: number;
}

type ActivityType = 'poll' | 'poker' | 'quiz' | 'wordcloud';
type ActivityStatus = 'draft' | 'active' | 'expired';
```

### Activity Components Structure
Each activity type requires four core components:

1. **ActivityConfig Interface** - Configuration schema for admin setup
2. **AdminEditor Component** - Admin interface for configuration
3. **ViewerDisplay Component** - Large screen display for live events
4. **ParticipantInterface Component** - Mobile interface for participation
5. **ResultProcessor** - Logic for aggregating and processing responses

## Activity State Machine

All activities follow the same lifecycle:

```
Draft → Active → Expired
  ↑       ↓
  └─── Edit ────┘
```

### State Transitions
```python
# Backend state management
class ActivityStateManager:
    def transition_to_active(self, activity_id: UUID) -> Activity:
        """Transition activity from draft to active"""
        # Validate configuration is complete
        # Set start timestamp
        # Notify all participants
        pass
    
    def transition_to_expired(self, activity_id: UUID) -> Activity:
        """Transition activity to expired (results-only)"""
        # Stop accepting new responses
        # Calculate final results
        # Update session state
        pass
```

### Frontend State Synchronization
```typescript
// Activity state hook for all personas
const useActivityState = (activityId: string) => {
  const { data: activity } = usePolling(`/api/activities/${activityId}`, {
    interval: 2000,
    enabled: !!activityId
  });
  
  return {
    activity,
    isActive: activity?.status === 'active',
    isExpired: activity?.status === 'expired',
    timeRemaining: calculateTimeRemaining(activity)
  };
};
```

## Activity Type Implementations

### 1. Poll Activity

**Configuration Schema:**
```typescript
interface PollConfig {
  question: string;
  options: PollOption[];
  allow_multiple: boolean;
  show_results_live: boolean;
}

interface PollOption {
  id: string;
  text: string;
  color?: string;
}
```

**Admin Editor:**
```typescript
const PollEditor = ({ activity, onChange }: ActivityEditorProps<PollConfig>) => {
  return (
    <ActivityEditorLayout title="Poll Configuration">
      <QuestionInput 
        value={activity.config.question}
        onChange={(question) => onChange({ ...activity.config, question })}
      />
      <OptionsEditor 
        options={activity.config.options}
        onAddOption={addOption}
        onRemoveOption={removeOption}
        onEditOption={editOption}
      />
      <SettingsPanel>
        <Checkbox 
          checked={activity.config.allow_multiple}
          onChange={(allow_multiple) => onChange({ ...activity.config, allow_multiple })}
        >
          Allow multiple selections
        </Checkbox>
        <Checkbox 
          checked={activity.config.show_results_live}
          onChange={(show_results_live) => onChange({ ...activity.config, show_results_live })}
        >
          Show live results
        </Checkbox>
      </SettingsPanel>
    </ActivityEditorLayout>
  );
};
```

**Participant Interface:**
```typescript
const PollParticipant = ({ activity, onSubmit }: ParticipantProps<PollConfig>) => {
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  
  return (
    <ParticipantLayout>
      <ActivityTitle>{activity.config.question}</ActivityTitle>
      <OptionsList>
        {activity.config.options.map(option => (
          <OptionButton
            key={option.id}
            selected={selectedOptions.includes(option.id)}
            onClick={() => toggleOption(option.id)}
            touchFriendly
          >
            {option.text}
          </OptionButton>
        ))}
      </OptionsList>
      <SubmitButton 
        onClick={() => onSubmit({ selectedOptions })}
        disabled={selectedOptions.length === 0}
      >
        Submit Vote
      </SubmitButton>
    </ParticipantLayout>
  );
};
```

**Viewer Display:**
```typescript
const PollViewer = ({ activity, responses }: ViewerProps<PollConfig>) => {
  const results = usePollResults(responses);
  
  return (
    <ViewerLayout>
      <LargeTitle>{activity.config.question}</LargeTitle>
      {activity.config.show_results_live && (
        <LiveChart 
          data={results}
          type="bar"
          animated
          largeText
        />
      )}
      <ParticipantCount count={responses.length} />
    </ViewerLayout>
  );
};
```

### 2. Planning Poker Activity

**Configuration Schema:**
```typescript
interface PokerConfig {
  story_title: string;
  story_description: string;
  scale: PokerScale;
  allow_reveal_all: boolean;
}

type PokerScale = 'fibonacci' | 'linear' | 'tshirt';
```

**Unique Features:**
- Private voting with simultaneous reveal
- Discussion phases between rounds
- Consensus tracking and re-voting

### 3. Quiz/Trivia Activity

**Configuration Schema:**
```typescript
interface QuizConfig {
  question: string;
  options: QuizOption[];
  correct_answer: string;
  explanation?: string;
  time_limit: number;
  points: number;
}

interface QuizOption {
  id: string;
  text: string;
  is_correct: boolean;
}
```

**Unique Features:**
- First-to-answer buzzer mechanics
- Scoring system with leaderboards
- Timed questions with countdown

### 4. Word Cloud Activity

**Configuration Schema:**
```typescript
interface WordCloudConfig {
  prompt: string;
  max_words: number;
  filter_profanity: boolean;
  word_limit_per_participant: number;
}
```

**Unique Features:**
- Real-time word aggregation
- Text filtering and moderation
- Dynamic visual updates

## Response Processing

### Generic Response Handler
```python
# Backend response processing
class ActivityResponseProcessor:
    def process_response(
        self, 
        activity_id: UUID, 
        participant_id: UUID, 
        response_data: dict
    ) -> ResponseResult:
        activity = self.get_activity(activity_id)
        
        # Validate response against activity config
        validator = self.get_validator(activity.type)
        if not validator.validate(response_data, activity.config):
            raise ValidationError("Invalid response format")
        
        # Store response
        response = self.store_response(activity_id, participant_id, response_data)
        
        # Update aggregated results
        self.update_results(activity_id)
        
        # Notify other participants if live results enabled
        if self.should_broadcast_update(activity):
            self.broadcast_update(activity_id)
        
        return ResponseResult(success=True, response=response)
```

### Frontend Response Submission
```typescript
const useActivityResponse = (activityId: string) => {
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  const submitResponse = async (responseData: any) => {
    setSubmitting(true);
    try {
      await api.post(`/api/activities/${activityId}/responses`, {
        response_data: responseData
      });
      setSubmitted(true);
    } catch (error) {
      // Handle error
    } finally {
      setSubmitting(false);
    }
  };
  
  return { submitResponse, submitted, submitting };
};
```

## Activity Registration System

### Activity Registry
```typescript
// Frontend activity registry
export const ACTIVITY_REGISTRY = {
  poll: {
    name: 'Poll',
    description: 'Multiple choice voting',
    AdminEditor: PollEditor,
    ViewerDisplay: PollViewer,
    ParticipantInterface: PollParticipant,
    configSchema: PollConfigSchema,
    icon: PollIcon
  },
  poker: {
    name: 'Planning Poker',
    description: 'Story point estimation',
    AdminEditor: PokerEditor,
    ViewerDisplay: PokerViewer,
    ParticipantInterface: PokerParticipant,
    configSchema: PokerConfigSchema,
    icon: PokerIcon
  },
  quiz: {
    name: 'Quiz',
    description: 'Knowledge testing',
    AdminEditor: QuizEditor,
    ViewerDisplay: QuizViewer,
    ParticipantInterface: QuizParticipant,
    configSchema: QuizConfigSchema,
    icon: QuizIcon
  },
  wordcloud: {
    name: 'Word Cloud',
    description: 'Collaborative word collection',
    AdminEditor: WordCloudEditor,
    ViewerDisplay: WordCloudViewer,
    ParticipantInterface: WordCloudParticipant,
    configSchema: WordCloudConfigSchema,
    icon: WordCloudIcon
  }
} as const;
```

### Dynamic Activity Rendering
```typescript
const ActivityRenderer = ({ activity, persona, ...props }: ActivityRendererProps) => {
  const activityDef = ACTIVITY_REGISTRY[activity.type];
  
  if (!activityDef) {
    throw new Error(`Unknown activity type: ${activity.type}`);
  }
  
  switch (persona) {
    case 'admin':
      const AdminComponent = activityDef.AdminEditor;
      return <AdminComponent activity={activity} {...props} />;
      
    case 'viewer':
      const ViewerComponent = activityDef.ViewerDisplay;
      return <ViewerComponent activity={activity} {...props} />;
      
    case 'participant':
      const ParticipantComponent = activityDef.ParticipantInterface;
      return <ParticipantComponent activity={activity} {...props} />;
      
    default:
      throw new Error(`Unknown persona: ${persona}`);
  }
};
```

## Testing Patterns for Activities

### Activity Component Testing
```typescript
// Test template for activity components
describe('PollActivity', () => {
  const mockActivity: Activity<PollConfig> = {
    id: 'test-id',
    type: 'poll',
    config: {
      question: 'Test question?',
      options: [
        { id: '1', text: 'Option 1' },
        { id: '2', text: 'Option 2' }
      ],
      allow_multiple: false,
      show_results_live: true
    }
  };
  
  describe('ParticipantInterface', () => {
    it('allows selecting options', () => {
      render(<PollParticipant activity={mockActivity} onSubmit={jest.fn()} />);
      
      fireEvent.click(screen.getByText('Option 1'));
      expect(screen.getByText('Option 1')).toHaveClass('selected');
    });
    
    it('submits response on button click', () => {
      const onSubmit = jest.fn();
      render(<PollParticipant activity={mockActivity} onSubmit={onSubmit} />);
      
      fireEvent.click(screen.getByText('Option 1'));
      fireEvent.click(screen.getByText('Submit Vote'));
      
      expect(onSubmit).toHaveBeenCalledWith({ selectedOptions: ['1'] });
    });
  });
});
```

### Backend Activity Testing
```python
# Test patterns for activity processing
def test_poll_response_processing():
    activity = create_test_poll_activity()
    participant = create_test_participant()
    
    response_data = {"selected_options": ["option_1"]}
    
    result = process_activity_response(
        activity.id, 
        participant.id, 
        response_data
    )
    
    assert result.success is True
    assert len(activity.responses) == 1
    assert activity.responses[0].response_data == response_data
```

## Extension Guidelines

### Adding New Activity Types
1. Define configuration schema with TypeScript interface
2. Implement all four required components (Admin, Viewer, Participant, Processor)
3. Add validation logic for response data
4. Register in activity registry
5. Add comprehensive tests
6. Update documentation

### Example New Activity Template
```typescript
// Template for new activity implementation
interface NewActivityConfig {
  // Define configuration options
}

const NewActivityEditor = ({ activity, onChange }: ActivityEditorProps<NewActivityConfig>) => {
  // Admin configuration interface
};

const NewActivityViewer = ({ activity, responses }: ViewerProps<NewActivityConfig>) => {
  // Large screen display
};

const NewActivityParticipant = ({ activity, onSubmit }: ParticipantProps<NewActivityConfig>) => {
  // Mobile participation interface
};

// Register the new activity
ACTIVITY_REGISTRY.newactivity = {
  name: 'New Activity',
  description: 'Description of new activity',
  AdminEditor: NewActivityEditor,
  ViewerDisplay: NewActivityViewer,
  ParticipantInterface: NewActivityParticipant,
  configSchema: NewActivityConfigSchema,
  icon: NewActivityIcon
};
```

This framework ensures consistency across all activity types while allowing for unique functionality and user experiences specific to each activity type.