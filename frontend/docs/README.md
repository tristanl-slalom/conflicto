# Caja Frontend - Multi-Persona Interface System

## Overview

The Caja frontend is a React-based interactive engagement platform built with TanStack Start,
designed to support three distinct persona interfaces: Admin, Viewer, and Participant. Each
interface is optimized for specific use cases and device types within the live event engagement
ecosystem.

## Architecture

### Technology Stack

- **Framework**: React 18+ with TypeScript
- **Routing**: TanStack Router with file-based routing
- **State Management**: TanStack Query for server state management
- **Styling**: Tailwind CSS with responsive design patterns
- **Components**: shadcn/ui component library
- **Build Tool**: Vite
- **Testing**: Jest with React Testing Library

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layouts/
│   │   │   └── PersonaLayout.tsx          # Reusable persona-specific layouts
│   │   └── ui/                            # shadcn/ui components
│   ├── hooks/
│   │   └── useSession.ts                  # Session management and real-time polling
│   ├── routes/
│   │   ├── __root.tsx                     # Root layout with navigation
│   │   ├── index.tsx                      # Landing page with persona selection
│   │   ├── admin/
│   │   │   └── index.tsx                  # Admin interface for session management
│   │   ├── viewer/
│   │   │   └── index.tsx                  # Viewer display for large screens
│   │   └── participant/
│   │       └── index.tsx                  # Participant interface (mobile-optimized)
│   └── __tests__/                         # Comprehensive test suite
└── package.json
```

## Multi-Persona System

### Admin Interface (`/admin`)

**Target Users**: Event organizers, facilitators, content managers

**Features**:

- Session configuration and creation
- Content management (questions, options, settings)
- Real-time participant monitoring
- Session lifecycle control (draft → active → completed)
- Analytics dashboard with results export

**Design Characteristics**:

- Desktop-optimized layout with multi-column interface
- Blue accent color scheme indicating control/authority
- Rich form controls and data visualization
- Comprehensive navigation and quick actions

### Viewer Interface (`/viewer`)

**Target Users**: Large screen displays, projectors, shared viewing

**Features**:

- Full-screen session display with live results
- QR code generation for easy participant joining
- Real-time result visualization with animations
- Large, readable typography for distance viewing
- Automatic content refresh every 2-3 seconds

**Design Characteristics**:

- Maximized content area with minimal chrome
- Green accent color scheme indicating "live/active"
- High contrast design for visibility
- Responsive scaling for various screen sizes

### Participant Interface (`/participant`)

**Target Users**: Event attendees on mobile devices

**Features**:

- Quick session joining via QR code or session ID
- Touch-optimized voting and interaction controls
- Real-time feedback submission
- Vote confirmation and status updates
- Minimal bandwidth usage for mobile networks

**Design Characteristics**:

- Mobile-first responsive design
- Purple accent color scheme indicating interaction/participation
- Large touch targets (minimum 44px)
- Simplified navigation and streamlined flows
- Offline-capable voting with sync when connected

## Component Architecture

### PersonaLayout Component

Provides consistent layout structure across all personas with customizable:

- Color schemes and branding per persona
- Navigation and header elements
- Responsive breakpoints and styling
- Shared UI patterns and components

```tsx
interface PersonaLayoutProps {
  persona: 'admin' | 'viewer' | 'participant';
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}
```

### Reusable Components

- **Card**: Consistent content containers with backdrop blur and borders
- **Button**: Multi-variant buttons with focus states and accessibility
- **Input/Select**: Form controls with proper labeling and validation
- **Loading States**: Skeleton loaders and progress indicators

## State Management

### Session Management Hook (`useSession`)

Handles all session-related state and API interactions:

```tsx
// Session data fetching
const { data: session, isLoading, error } = useSession(sessionId);

// Session creation and updates
const createSession = useCreateSession();
const updateSession = useUpdateSession();

// Real-time response polling
const { data: responses } = useSessionResponses(sessionId, enabled);
```

### Participant Management Hook

Manages participant state and local storage:

```tsx
const { participantId, currentSessionId, joinSession, leaveSession } = useParticipantSession();
```

### Polling-Based Synchronization

Implements 2-3 second polling intervals for real-time updates without WebSockets:

```tsx
const usePolling = (callback: () => void, interval = 3000, enabled = true)
```

## Responsive Design

### Breakpoint Strategy

- **Mobile First**: Base styles target 375px+ devices
- **Tablet**: `md:` (768px+) for moderate screen sizes
- **Desktop**: `lg:` (1024px+) for full desktop experiences
- **Large Desktop**: `xl:` (1280px+) for enhanced layouts

### Persona-Specific Responsiveness

**Admin Interface**:

- Single column layout on mobile
- Multi-column dashboard on desktop
- Collapsible sidebars and panels

**Viewer Interface**:

- Scales content proportionally across all sizes
- Maintains readability at distance
- Adapts QR code size to screen real estate

**Participant Interface**:

- Optimized for one-handed mobile use
- Large touch targets and simplified navigation
- Progressive enhancement for larger screens

## Real-Time Features

### Polling Implementation

- **Query Invalidation**: TanStack Query automatically refetches stale data
- **Optimistic Updates**: Immediate UI feedback for user actions
- **Error Handling**: Graceful degradation when network is unavailable
- **Background Sync**: Continues polling when app is backgrounded

### Performance Optimizations

- **Selective Polling**: Only active sessions poll for updates
- **Debounced Updates**: Prevents excessive re-renders from rapid changes
- **Cached Results**: Stale-while-revalidate pattern reduces load times
- **Incremental Updates**: Only fetch changed data when possible

## Accessibility

### WCAG 2.1 AA Compliance

- **Color Contrast**: All text meets 4.5:1 contrast ratio minimum
- **Keyboard Navigation**: Full keyboard accessibility for all interactive elements
- **Screen Readers**: Proper ARIA labels and semantic HTML structure
- **Focus Management**: Clear focus indicators and logical tab order

### Mobile Accessibility

- **Touch Targets**: Minimum 44px target size for interactive elements
- **Zoom Support**: Interface remains functional at 200% zoom
- **Voice Control**: Compatible with voice navigation systems
- **Reduced Motion**: Respects `prefers-reduced-motion` setting

## Testing Strategy

### Unit Tests

- **Component Rendering**: All components render correctly with props
- **User Interactions**: Click, input, and form submission behaviors
- **State Management**: Hook behavior and state transitions
- **Error Boundaries**: Graceful handling of component failures

### Integration Tests

- **Multi-Persona Flow**: Complete user journeys across interfaces
- **Real-Time Sync**: Polling and data synchronization behavior
- **Responsive Behavior**: Layout adaptation across breakpoints
- **API Integration**: Mock API interactions and error scenarios

### Performance Tests

- **Bundle Size**: JavaScript bundle optimization and code splitting
- **Render Performance**: Component update cycles and virtual DOM efficiency
- **Network Usage**: Polling frequency and data transfer optimization
- **Memory Usage**: Prevention of memory leaks in long-running sessions

## Deployment and Build

### Build Configuration

```json
{
  "scripts": {
    "dev": "vinxi dev",
    "build": "vinxi build",
    "start": "vinxi start",
    "test": "jest",
    "test:coverage": "jest --coverage"
  }
}
```

### Environment Configuration

- **Development**: Hot reload, development tools, mock data
- **Staging**: Production build with staging API endpoints
- **Production**: Optimized build, CDN assets, analytics tracking

## Security Considerations

### Client-Side Security

- **XSS Prevention**: Sanitized user input and content rendering
- **CSRF Protection**: Token-based request authentication
- **Secure Storage**: Sensitive data handled via secure storage APIs
- **Content Security Policy**: Strict CSP headers to prevent injection attacks

### Session Security

- **Session Validation**: Server-side session state verification
- **Rate Limiting**: Protection against rapid-fire voting or spam
- **Input Validation**: Client and server-side data validation
- **Audit Logging**: User actions logged for security monitoring

## Future Enhancements

### Planned Features

- **WebSocket Support**: Real-time bidirectional communication
- **Offline Mode**: Progressive Web App with offline capabilities
- **Advanced Analytics**: Detailed engagement metrics and reporting
- **Customizable Themes**: Brand customization for different organizations
- **Multi-Language Support**: Internationalization and localization

### Technical Improvements

- **Micro-Frontend Architecture**: Independently deployable persona interfaces
- **Edge Computing**: CDN-based real-time data synchronization
- **Advanced Caching**: Service Worker-based intelligent caching
- **Performance Monitoring**: Real User Monitoring (RUM) integration

## API Integration

### Expected Backend Endpoints

```typescript
// Session Management
POST /api/sessions - Create new session
GET /api/sessions/:id - Retrieve session details
PUT /api/sessions/:id - Update session
DELETE /api/sessions/:id - Delete session

// Participant Management
POST /api/sessions/:id/join - Join session
POST /api/sessions/:id/vote - Submit vote
GET /api/sessions/:id/results - Get real-time results

// Real-time Updates
GET /api/sessions/:id/poll - Polling endpoint for updates
```

### Data Models

```typescript
interface Session {
  id: string;
  name: string;
  type: 'poll' | 'quiz' | 'poker' | 'wordcloud';
  status: 'draft' | 'active' | 'completed';
  question: string;
  options: string[];
  participantCount: number;
  createdAt: string;
  updatedAt: string;
}

interface SessionResponse {
  optionIndex: number;
  count: number;
  percentage: number;
}
```

This frontend implementation provides a solid foundation for the Caja interactive engagement
platform, with scalable architecture, comprehensive testing, and clear separation of concerns across
the multi-persona interface system.
