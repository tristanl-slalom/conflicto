# Implementation Plan: Pre-Lobby Landing Page for Draft Sessions with Live Attendee List

**GitHub Issue:** [#78](https://github.com/tristanl-slalom/conflicto/issues/78)
**Generated:** 2025-10-08T20:45:00Z

## Implementation Strategy

### High-Level Approach

This feature extends the existing participant experience by adding a pre-lobby state for draft sessions. **Importantly, the backend already supports participants joining draft sessions and provides session status in API responses.** The implementation focuses on frontend UI changes to provide a better waiting experience.

**Key Strategy Points:**
1. **Leverage Existing Backend**: Current participant APIs already handle draft sessions correctly
2. **Frontend-Only Changes**: No backend modifications needed - session status is already provided
3. **Status-Based UI Logic**: Implement conditional rendering based on session status from existing APIs
4. **Polling Integration**: Extend existing real-time patterns for pre-lobby updates using current endpoints
5. **Mobile-First Design**: Ensure optimal experience for QR code scanning users
6. **Seamless Transitions**: Smooth progression from pre-lobby to active session using existing status polling

### Backend Reality Check

After analyzing the current backend implementation:
- ✅ **Participants can already join draft sessions** via existing `/join` endpoint
- ✅ **Session status is included** in join response and heartbeat responses  
- ✅ **Participant status computation** already works for participants in draft sessions
- ✅ **Status transitions** are automatically handled when session moves to active
- ✅ **No database changes needed** - all required data is already available
- ✅ **No API changes needed** - existing endpoints provide all necessary information

## File Structure Changes

### New Files to Create

#### Frontend Components
```
frontend/src/components/
├── lobby/
│   ├── PreLobbyLandingPage.tsx      # Main pre-lobby component
│   ├── PreLobbyParticipantList.tsx  # Participant list for pre-lobby
│   └── SessionStatusIndicator.tsx   # Status indicator component
└── participant/
    └── ParticipantSessionWrapper.tsx # Wrapper for session status detection
```

#### Additional Support Files
```
frontend/src/
├── hooks/
│   └── useSessionStatus.ts         # Hook for session status management
└── types/
    └── lobby.ts                     # Type definitions for lobby components
```

### Files to Modify

#### Frontend Modifications
```
frontend/src/
├── routes/join/$sessionId.tsx       # Add pre-lobby routing logic based on session status
├── components/
│   ├── SessionJoin.tsx             # Redirect to pre-lobby after join if session is draft
│   └── ParticipantList.tsx         # Potential styling updates for pre-lobby context
└── types/index.ts                  # Export new lobby types
```

#### Testing Files to Create/Modify
```
frontend/src/components/lobby/
├── __tests__/
│   ├── PreLobbyLandingPage.test.tsx
│   ├── PreLobbyParticipantList.test.tsx
│   └── SessionStatusIndicator.test.tsx
└── __mocks__/
    └── sessionData.ts              # Mock data for testing
```

**No Backend Changes Required** - All necessary functionality already exists in the current participant service and APIs.

## Implementation Steps

### Step 1: Create Core Pre-Lobby Components
**Files**: `PreLobbyLandingPage.tsx`, `PreLobbyParticipantList.tsx`, `SessionStatusIndicator.tsx`

1. **PreLobbyLandingPage Component**
   - Create main component that displays when session status is `draft`
   - Integrate session information display (title, description)
   - Add participant count display with live updates
   - Implement "Waiting for session to start" messaging
   - Include session status polling for transition detection

2. **PreLobbyParticipantList Component**
   - Extend existing `ParticipantList` patterns for pre-lobby context
   - Display participant nicknames with status indicators
   - Show join timestamps and participant count
   - Implement real-time polling (2-3 second intervals)
   - Add mobile-optimized responsive layout

3. **SessionStatusIndicator Component**
   - Create reusable status indicator for session state
   - Display clear messaging for draft/waiting state
   - Include visual indicators (icons, colors)
   - Support different status types for future use

### Step 2: Implement Session Status Detection Hook
**Files**: `useSessionStatus.ts`, `ParticipantSessionWrapper.tsx`

1. **useSessionStatus Hook**
   - Create hook that uses existing session and heartbeat APIs for status detection
   - **Key insight**: Session status is already provided in join response and heartbeat responses
   - Handle status transitions (draft → active → completed) using existing data
   - Provide loading states and error handling for API calls
   - Return session status from existing API responses (no new endpoints needed)

2. **ParticipantSessionWrapper Component**
   - Create wrapper component for status-based UI rendering
   - Implement conditional rendering: PreLobbyLandingPage for draft, existing UI for active
   - Handle transitions between pre-lobby and active session seamlessly
   - Manage participant state across status changes using existing participant context
   - Provide error boundaries for status detection failures

### Step 3: Update Join Flow and Routing
**Files**: `join/$sessionId.tsx`, `SessionJoin.tsx`

1. **Join Route Enhancement**
   - Modify join route to check session status after successful join
   - Redirect to pre-lobby component if session is in draft status
   - Redirect to active session if session is already active
   - Handle join failures and status detection errors
   - Maintain existing QR code scanning functionality

2. **SessionJoin Component Updates**
   - Update post-join flow to handle status-based redirects
   - Add loading states during status detection
   - Maintain existing nickname validation and join logic
   - Provide clear messaging during join and redirect process

### Step 4: Implement Real-time Polling and State Management
**Files**: Modify existing polling patterns in components

1. **Polling Integration**
   - **Use existing TanStack Query patterns** for session data and participant lists
   - **Leverage existing endpoints**: No new APIs needed for status or participant data
   - Implement 2-3 second polling intervals for:
     - Session status changes (via existing session endpoint)
     - Participant list updates (via existing participants endpoint)  
     - Participant status changes (via existing participant status computation)
   - Add optimistic updates for real-time feel using existing patterns
   - Handle polling errors and network interruptions with current error handling

2. **State Synchronization**
   - Ensure participant state consistency across status transitions using existing participant management
   - **Key insight**: Existing heartbeat system already maintains participant state across session status changes
   - Handle participant heartbeat continuity (already implemented in backend)
   - Manage local storage for participant session data (leverage existing patterns)

### Step 5: Mobile-Responsive Design Implementation
**Files**: All component files with CSS/styling

1. **Mobile-First Layout**
   - Implement responsive design for QR code scanning devices
   - Optimize touch targets for mobile interaction
   - Ensure readability across different screen sizes
   - Test on common mobile devices and browsers

2. **UI/UX Polish**
   - Apply Caja design system patterns and colors
   - Implement smooth loading states and transitions
   - Add appropriate spacing and typography

### Step 6: Add Type Definitions and Testing
**Files**: `types/lobby.ts`, test files

1. **Type Definitions**
   - Create TypeScript types for pre-lobby components
   - Define interfaces for session status management
   - Add props types for all new components
   - Export types for use across the application

2. **Component Testing**
   - Write unit tests for all new components
   - Test status detection and routing logic
   - Mock API calls for polling and session status
   - Test responsive design at different breakpoints
   - Verify accessibility features with testing tools

### Step 7: Integration Testing and Edge Cases
**Files**: Integration test files, error handling improvements

1. **Integration Testing**
   - Test full join-to-pre-lobby-to-active-session flow
   - Verify real-time updates with multiple participants
   - Test session status transitions with concurrent users
   - Validate performance with 50+ participants in pre-lobby

2. **Edge Case Handling**
   - Handle session status changes during pre-lobby display
   - Manage participant disconnections and reconnections
   - Handle API failures gracefully

## Testing Strategy

### Unit Testing
- **Component Tests**: Test rendering, props, and user interactions
- **Hook Tests**: Test `useSessionStatus` hook logic and state management
- **Utility Tests**: Test helper functions and type conversions
- **Polling Tests**: Mock polling behavior and test update frequencies

### Integration Testing
- **Join Flow Tests**: Test complete participant onboarding to pre-lobby
- **Status Transition Tests**: Test transitions from draft to active sessions
- **Real-time Update Tests**: Test participant list updates and status changes
- **Error Handling Tests**: Test API failures and network interruptions

### End-to-End Testing
- **QR Code Flow**: Test QR code scanning to pre-lobby experience
- **Multiple Participants**: Test concurrent participant join scenarios
- **Session Lifecycle**: Test complete session flow from draft to completion
- **Mobile Experience**: Test on actual mobile devices with QR codes

### Performance Testing
- **Polling Performance**: Test polling efficiency with multiple participants
- **Memory Usage**: Monitor memory consumption during long pre-lobby sessions
- **Network Efficiency**: Test bandwidth usage with frequent polling
- **Concurrent Users**: Test system performance with 50+ participants

## Deployment Considerations

### Database Changes
**No database migrations required** - Implementation uses existing participant and session tables without modifications.

### Environment Variables
**No new environment variables needed** - Uses existing API configuration and polling settings.

### Configuration Changes
**No configuration file changes required** - Leverages existing polling intervals, API endpoints, and session management settings.

### Frontend Build Changes
- Update component exports in main index files
- Ensure new types are properly exported
- Verify build process includes new component files
- Test production build with minification

### API Compatibility
**No API changes required** - All necessary data is already available through:
- Existing session endpoints provide session status
- Existing participant endpoints provide participant lists and status
- Existing join endpoint supports draft sessions
- Existing heartbeat endpoint includes session status in activity context

## Risk Assessment

### Potential Issues and Mitigation Strategies

#### Technical Risks
1. **Polling Performance Risk**
   - *Issue*: Increased polling load with pre-lobby participants
   - *Mitigation*: Use existing optimized polling patterns, monitor performance metrics
   - *Fallback*: Implement fallback polling intervals or disable real-time updates

2. **Session Status Race Conditions**
   - *Issue*: Status changes during pre-lobby display causing confusion
   - *Mitigation*: Implement proper loading states and atomic status checks
   - *Fallback*: Force page refresh on status detection failures

3. **Mobile Performance Issues**
   - *Issue*: Poor performance on older mobile devices
   - *Mitigation*: Optimize component rendering and minimize DOM updates
   - *Fallback*: Provide lightweight fallback interface for slow devices

#### User Experience Risks
1. **Confusing Transition States**
   - *Issue*: Users may be confused during status transitions
   - *Mitigation*: Clear messaging and smooth visual transitions
   - *Fallback*: Simple redirect with loading indicator

2. **Empty Pre-Lobby Experience**
   - *Issue*: Single participant may feel isolated in empty pre-lobby
   - *Mitigation*: Clear messaging about waiting for other participants
   - *Fallback*: Option to send invite links or return to join screen

#### API Integration Risks
1. **Participant API Changes**
   - *Issue*: Existing participant APIs may change
   - *Mitigation*: Comprehensive testing and error boundary implementation
   - *Fallback*: Graceful degradation to basic participant list

## Estimated Effort

### Development Time Estimation

#### Component Development (3-4 days)
- **PreLobbyLandingPage**: 1 day
- **PreLobbyParticipantList**: 1 day  
- **SessionStatusIndicator**: 0.5 days
- **useSessionStatus Hook**: 0.5 days
- **ParticipantSessionWrapper**: 1 day

#### Integration and Testing (2-3 days)
- **Join Flow Updates**: 1 day
- **Routing Logic**: 0.5 days
- **Unit Testing**: 1 day
- **Integration Testing**: 0.5 days

#### Polish and Documentation (1-2 days)
- **Mobile Responsive Design**: 1 day
- **Accessibility Testing**: 0.5 days
- **Documentation Updates**: 0.5 days

### Total Estimated Effort: 6-9 days

### Complexity Assessment
- **Low Complexity**: Leverages existing infrastructure and patterns
- **Medium Risk**: Requires careful status transition handling
- **High Value**: Significantly improves participant experience

### Prerequisites
- Existing participant management system must be stable
- Current polling infrastructure should handle additional load
- Session status management should be reliable and immediate

### Success Metrics
- Smooth participant experience in pre-lobby state
- Real-time participant list updates working reliably
- Seamless transitions from draft to active session status
- Positive user feedback on waiting room experience
- No performance degradation with increased polling load