# User Personas & Interface Guidelines

## Three-Persona System

The Caja platform serves three distinct user types, each with specific interface requirements and interaction patterns.

## Admin Persona

### Purpose
Configure sessions and activities before launch. Manage content and session settings.

### Interface Requirements
- **Platform:** Desktop-optimized with comprehensive controls
- **Screen Size:** Large desktop displays (1440px+)
- **Interaction:** Mouse and keyboard, form-heavy interfaces

### Key Actions
- Create and name sessions
- Configure activity sequences and ordering
- Set up activity-specific content (questions, options, etc.)
- Preview activities before launch
- Manage session lifecycle (draft → active → completed)

### UI Design Rules
```typescript
// Admin interface components should follow these patterns:

// Form-based interfaces with validation
interface AdminFormProps {
  onSubmit: (data: FormData) => void;
  validation: ValidationSchema;
  showSaveState: boolean;
}

// Multi-step workflows with clear progression
interface WorkflowStepProps {
  currentStep: number;
  totalSteps: number;
  onNext: () => void;
  onPrevious: () => void;
  canProceed: boolean;
}
```

### Design Principles
- Use form-based interfaces with real-time validation
- Provide preview modes for all activities
- Include draft/publish workflows with clear state indicators
- Show clear save states and error messages
- Use tabs or accordion patterns for complex configuration
- Implement undo/redo functionality where appropriate
- Provide bulk actions for managing multiple activities

### Example Component Structure
```typescript
// AdminDashboard.tsx
const AdminDashboard = () => {
  return (
    <Layout sidebar={<NavigationSidebar />}>
      <Header title="Session Management" />
      <Tabs>
        <TabPanel label="Sessions">
          <SessionList />
          <CreateSessionButton />
        </TabPanel>
        <TabPanel label="Activities">
          <ActivityLibrary />
        </TabPanel>
        <TabPanel label="Analytics">
          <SessionAnalytics />
        </TabPanel>
      </Tabs>
    </Layout>
  );
};
```

## Viewer/Runner Persona

### Purpose
Display session content on large screen and control session flow during live events.

### Interface Requirements
- **Platform:** Large screen optimized (TV, projector, large monitor)
- **Screen Size:** 1080p+ displays, optimized for viewing from distance
- **Interaction:** Simple controls, often operated via laptop/tablet

### Key Actions
- Display current activity content prominently
- Show live results and participant responses
- Control progression between activities
- Display persistent QR code for joining
- Monitor participant engagement

### UI Design Rules
```typescript
// Viewer components prioritize visibility and simplicity
interface ViewerDisplayProps {
  activity: Activity;
  participants: Participant[];
  showQRCode: boolean;
  results?: ActivityResults;
}

// Large, readable text and visual elements
const ViewerStyles = {
  heading: "text-6xl font-bold mb-8",
  body: "text-3xl leading-relaxed",
  qrCode: "fixed bottom-4 right-4 w-32 h-32",
  results: "text-4xl font-semibold text-center"
};
```

### Design Principles
- Large text and visual elements for visibility from distance
- Persistent small QR code in corner for late participants
- Prominent activity content with live result updates
- Simple next/previous controls for session runner
- Minimal UI chrome - focus on content
- High contrast colors for readability
- Auto-advance timers with clear visual countdown
- Real-time animations for engagement

### Example Component Structure
```typescript
// ViewerDisplay.tsx
const ViewerDisplay = ({ session, currentActivity }: ViewerProps) => {
  return (
    <FullScreenLayout>
      <ActivityDisplay
        activity={currentActivity}
        showTimer={true}
        fontSize="large"
      />
      <LiveResults
        responses={currentActivity.responses}
        animated={true}
      />
      <QRCodeOverlay
        sessionId={session.id}
        position="bottom-right"
      />
      <RunnerControls
        onNext={advanceActivity}
        onPrevious={previousActivity}
        hidden={!isRunner}
      />
    </FullScreenLayout>
  );
};
```

## Participant Persona

### Purpose
Interact with activities on personal mobile device during live events.

### Interface Requirements
- **Platform:** Mobile-first responsive design
- **Screen Size:** Primarily mobile phones (320px - 428px width)
- **Interaction:** Touch-based, thumb-friendly interface

### Key Actions
- Join session via QR code scan
- Enter nickname for session
- Participate in current activity
- View personal response confirmation
- See live results (when appropriate)

### UI Design Rules
```typescript
// Mobile-first component design
interface ParticipantProps {
  activity: Activity;
  onSubmit: (response: Response) => void;
  disabled?: boolean;
}

// Touch-friendly sizing
const MobileStyles = {
  touchTarget: "min-h-[44px] min-w-[44px]", // 44px minimum
  button: "py-4 px-6 text-lg font-medium",
  input: "text-lg py-3 px-4",
  spacing: "space-y-4" // Generous spacing between elements
};
```

### Design Principles
- Thumb-friendly touch targets (44px minimum)
- Single-screen interactions with minimal scrolling
- Clear call-to-action buttons with high contrast
- Real-time feedback for submissions
- Progressive disclosure - show only what's needed
- Offline-first approach with graceful degradation
- Fast loading and responsive interactions
- Accessible color contrast and font sizes

### Example Component Structure
```typescript
// ParticipantInterface.tsx
const ParticipantInterface = ({ session, participant }: ParticipantProps) => {
  const currentActivity = useCurrentActivity(session.id);

  return (
    <MobileLayout>
      <SessionHeader
        sessionName={session.name}
        participantName={participant.nickname}
      />
      <ActivityInterface
        activity={currentActivity}
        onResponse={submitResponse}
        touchOptimized={true}
      />
      <ResponseFeedback
        submitted={hasSubmitted}
        showResults={activity.showResults}
      />
    </MobileLayout>
  );
};
```

## Cross-Persona Shared Components

### Common Patterns
All personas share certain interaction patterns and components:

```typescript
// Shared activity interface patterns
interface BaseActivityProps {
  activity: Activity;
  persona: 'admin' | 'viewer' | 'participant';
  readonly?: boolean;
}

// Responsive activity renderer
const ActivityRenderer = ({ activity, persona }: BaseActivityProps) => {
  switch (persona) {
    case 'admin':
      return <AdminActivityEditor activity={activity} />;
    case 'viewer':
      return <ViewerActivityDisplay activity={activity} />;
    case 'participant':
      return <ParticipantActivityInterface activity={activity} />;
  }
};
```

### State Synchronization
All personas must stay synchronized with session state:

```typescript
// Shared polling hook for all personas
const useSessionSync = (sessionId: string, persona: PersonaType) => {
  const pollingInterval = persona === 'participant' ? 2000 : 1000;

  return usePolling(`/api/sessions/${sessionId}/state`, {
    interval: pollingInterval,
    dependencies: [sessionId]
  });
};
```

## Accessibility Guidelines

### Universal Design Principles
- WCAG 2.1 AA compliance across all personas
- Keyboard navigation support (especially admin interface)
- Screen reader compatibility
- High contrast mode support
- Reduced motion preferences
- Focus management for dynamic content updates

### Persona-Specific Accessibility
- **Admin:** Full keyboard navigation, screen reader labels for complex forms
- **Viewer:** High contrast for distance viewing, optional audio cues
- **Participant:** Voice input support, haptic feedback, large touch targets

## Responsive Breakpoints

```css
/* Tailwind CSS breakpoints aligned with persona needs */
.mobile-first {
  /* Participant mobile: 320px - 768px */
  @apply text-lg py-3;
}

@media (min-width: 768px) {
  /* Participant tablet / Admin small: 768px - 1024px */
  .responsive {
    @apply text-xl py-4;
  }
}

@media (min-width: 1024px) {
  /* Admin desktop: 1024px+ */
  .desktop {
    @apply text-2xl py-6;
  }
}

@media (min-width: 1440px) {
  /* Viewer large screen: 1440px+ */
  .large-screen {
    @apply text-4xl py-8;
  }
}
```

## Performance Considerations

### Persona-Specific Optimizations
- **Admin:** Rich interactions, can handle larger bundle sizes
- **Viewer:** Optimize for smooth animations and real-time updates
- **Participant:** Minimize bundle size, optimize for slow connections

### Loading Strategies
```typescript
// Code splitting for persona-specific routes
const AdminApp = lazy(() => import('./admin/AdminApp'));
const ViewerApp = lazy(() => import('./viewer/ViewerApp'));
const ParticipantApp = lazy(() => import('./participant/ParticipantApp'));

// Persona detection and routing
const AppRouter = () => {
  const persona = detectPersona(); // Based on route or query params

  return (
    <Suspense fallback={<LoadingSpinner />}>
      {persona === 'admin' && <AdminApp />}
      {persona === 'viewer' && <ViewerApp />}
      {persona === 'participant' && <ParticipantApp />}
    </Suspense>
  );
};
```
