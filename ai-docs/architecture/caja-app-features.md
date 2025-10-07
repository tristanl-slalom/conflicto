# Caja App - High-Level Features

## User Journey Overview

The Caja platform follows a structured flow that supports three main personas through a complete session lifecycle:

### High-Level Session Flow (Based on Miro Diagram)
1. **Admin Setup Phase** (Red flow)
   - Admin defines session and configures activities in desired order
   - Session remains in draft state until ready to launch
   - Activities are pre-configured with specific settings and content

2. **Session Launch Phase**
   - Admin opens/starts the session, transitioning it to active state
   - Viewer displays session start screen with prominent QR code
   - System generates unique session join URL and QR code

3. **Participant Onboarding Phase** (Purple flow)
   - Participants scan QR code to connect to session
   - Participants enter nickname for session identification
   - System validates nickname uniqueness within session

4. **Activity Execution Phase** (Purple flow continuation)
   - Participants proceed through configured activities in sequence
   - Each activity follows the pattern: display → participate → results
   - Activities include: Pointing Poker, Polls, Word Clouds, Trivia
   - Small persistent QR code remains visible for late participants to join
   - Polling-based updates provide near real-time synchronization

5. **Session Completion Phase** (Blue flow)
   - After final activity, system proceeds to summary view
   - Summary includes participation metrics, activity results, and analytics
   - Session transitions to completed state with historical data preserved

This flow ensures a seamless experience from setup through completion, with clear role separation and consistent state management throughout the session lifecycle.

---

## Core Platform Features

### 1. Session Management
**Description:** Core functionality for creating, managing, and running event sessions with ordered activity sequences.

**Key Components:**
- Session lifecycle management (draft → active → completed)
- Ordered activity sequence configuration and execution
- QR code generation for participant joining
- Participant nickname registration and management
- Session state persistence and recovery
- Automatic progression through activity sequence
- Session summary generation upon completion

**User Stories Foundation:**
- As an admin, I can create a session and define the order of activities
- As an admin, I can open a session to make it available for participants
- As a participant, I can scan a QR code to join an active session
- As a participant, I can enter a nickname when joining a session
- As a viewer, I can display session information and QR codes on a shared screen
- As a system, I can automatically progress through activities and generate summaries

### 2. Activity Framework
**Description:** Extensible system for different types of interactive activities within sessions.

**Key Components:**
- Generic activity template system
- Activity states: draft → published → active → expired
- Activity-specific metadata and configuration
- Real-time state synchronization across all participants
- Activity timeout and progression controls

**User Stories Foundation:**
- As an admin, I can configure activity-specific content and rules
- As a viewer/runner, I can progress through activities and control timing
- As a participant, I can interact with the current activity on my device
- As a system, I can enforce activity rules and timeouts

### 3. Multi-Persona Interface System ✅ **IMPLEMENTED**
**Description:** Distinct user interfaces optimized for different roles and devices.

**Key Components:**
- **Admin Interface:** Session and activity configuration, content management ✅
- **Viewer/Runner Interface:** Large screen display with persistent QR code, session control, live results ✅
- **Participant Interface:** Mobile-first interaction, activity-specific controls ✅
- Dynamic interface updates based on activity type and state
- Persistent join access through always-visible QR code ✅

**Technical Implementation:**
- **Framework:** React 18+ with TypeScript and TanStack Start
- **Routing:** File-based routing with `/admin`, `/viewer`, `/participant` paths
- **Components:** Reusable PersonaLayout with theme-specific styling
- **State Management:** TanStack Query for server state with polling intervals
- **UI Library:** shadcn/ui components with Tailwind CSS
- **Testing:** Comprehensive Vitest test suite covering all personas

**User Stories Foundation:**
- As an admin, I can set up content without interfering with live sessions ✅
- As a viewer/runner, I can display session content with a persistent QR code for joining ✅
- As a participant, I can easily interact on my mobile device ✅
- As a late arrival, I can join the session by scanning the always-visible QR code ✅
- As a user, I can switch between roles as needed ✅

### 5. Polling-Based Synchronization Engine ✅ **FRONTEND IMPLEMENTED**
**Description:** Near real-time synchronization of activity states, participant actions, and results using efficient polling with generated API clients.

**Key Components:**
- Client-side polling for state updates (every 2-3 seconds) ✅
- Generated API hooks with automatic caching and invalidation ✅
- SPA-compatible state management with browser-based persistence ✅
- Type-safe API integration ready for backend connection ✅
- MSW mock infrastructure for comprehensive testing ✅
- Error handling and retry logic built into generated hooks ✅
- Optimized for static hosting (S3/CloudFront) deployment ✅

**Technical Implementation:**
- **Frontend Polling:** TanStack Query configured with 2-3 second refetch intervals in SPA mode
- **Generated API Hooks:** `useListSessionsApiV1SessionsGet`, `useCreateSessionApiV1SessionsPost` ready for backend
- **SPA Architecture:** Client-side routing and state management optimized for static deployment
- **Mock Implementation:** Complete MSW mock system with Faker.js for realistic development data
- **Error Handling:** Query retry logic and error boundaries implemented and tested
- **Static Deployment:** Compatible with AWS S3 + CloudFront CDN architecture

**User Stories Foundation:**
- As a participant, I can see updates within seconds without manual refresh ✅ (SPA Ready)
- As a viewer, I can see results update as participants respond (with slight delay) ✅ (SPA Ready)
- As a system, I can handle network interruptions gracefully with retry logic ✅
- As a developer, I can test all functionality without backend dependency ✅
- As a deployment system, I can serve the app from static CDN infrastructure ✅

### 5. QR Code and Participant Onboarding
**Description:** Seamless participant joining process through persistent QR code display and nickname registration.

**Key Components:**
- Dynamic QR code generation for active sessions
- Persistent small QR code display throughout all session activities
- Mobile-optimized joining interface
- Nickname validation and uniqueness checking
- Participant connection status tracking
- Graceful handling of late joiners mid-session
- Connection recovery for dropped participants
- Activity state synchronization for new joiners

**User Stories Foundation:**
- As a viewer, I can display a persistent QR code that allows joining at any time
- As a participant, I can scan a QR code to join even after activities have started
- As a participant, I can choose a unique nickname for the session
- As a late joiner, I can see the current activity state when I connect
- As a system, I can validate nicknames and handle duplicates gracefully
- As an admin, I can see who has joined the session in real-time
- As a participant, I can rejoin if my connection is lost

## Activity Type Features

### 6. Live Polling System
**Description:** Real-time polling with multiple question types and live result display.

**Key Components:**
- Multiple choice, text input, and rating scale questions
- Live result visualization (pie charts, bar graphs, word clouds)
- Anonymous and identified response modes
- Response validation and content filtering

**User Stories Foundation:**
- As an admin, I can create polls with various question types
- As a participant, I can vote and see my response confirmed
- As a viewer, I can see live poll results as votes come in
- As a system, I can validate and moderate participant responses

### 7. Planning Poker System
**Description:** Story point estimation with team consensus features.

**Key Components:**
- Fibonacci sequence voting options
- Reveal-all-at-once mechanics
- Discussion rounds and re-voting
- Result consensus tracking

**User Stories Foundation:**
- As a team member, I can submit story point estimates privately
- As a facilitator, I can reveal all votes simultaneously
- As a team, I can discuss estimates and re-vote if needed
- As a system, I can track consensus and suggest next steps

### 8. Interactive Quiz/Trivia System
**Description:** Knowledge Bowl style questions with buzzer mechanics and scoring.

**Key Components:**
- Question display with timed reveals
- First-to-buzz participant tracking
- Multi-round scoring system
- Question bank management

**User Stories Foundation:**
- As a participant, I can buzz in to answer questions
- As a viewer, I can see who buzzed in first and manage responses
- As an admin, I can create question banks and set up quiz rounds
- As a system, I can track scores and determine winners

### 9. Word Cloud Generator
**Description:** Real-time word cloud creation from participant text input.

**Key Components:**
- Text input collection and processing
- Live word frequency analysis
- Dynamic word cloud visualization
- Text filtering and moderation

**User Stories Foundation:**
- As a participant, I can submit text responses to prompts
- As a viewer, I can see word clouds update in real-time
- As an admin, I can set up prompts and configure word cloud settings
- As a system, I can filter inappropriate content

## Advanced Features

### 10. Content Moderation System
**Description:** Automated and manual content filtering for user-generated content.

**Key Components:**
- AI-powered content analysis
- Profanity and inappropriate content filtering
- Admin moderation dashboard
- Escalation and review workflows

**User Stories Foundation:**
- As a system, I can automatically flag inappropriate content
- As an admin, I can review and moderate flagged content
- As a participant, my content is filtered before public display
- As a viewer, I can trust that displayed content is appropriate

### 11. Session Analytics and Reporting
**Description:** Engagement metrics, participation tracking, and session summaries.

**Key Components:**
- Participation rate tracking
- Response time analytics
- Engagement sentiment analysis
- Exportable session reports
- Historical data comparison

**User Stories Foundation:**
- As an admin, I can see detailed engagement metrics after sessions
- As a facilitator, I can track participation rates during activities
- As an organization, I can measure event engagement over time
- As a system, I can provide actionable insights on session effectiveness

### 12. Live Reaction System
**Description:** Continuous emoji-based feedback throughout sessions.

**Key Components:**
- Always-available reaction interface
- Real-time sentiment visualization
- Reaction aggregation and trending
- Session-wide emotional pulse tracking

**User Stories Foundation:**
- As a participant, I can react with emojis throughout the session
- As a viewer, I can see live sentiment trends during presentations
- As a presenter, I can gauge audience engagement in real-time
- As an admin, I can analyze emotional responses to different content

### 13. Photo Sharing Activity
**Description:** Live photo board for visual engagement and icebreaking.

**Key Components:**
- Image upload and display system
- Photo moderation and filtering
- Live photo gallery interface
- Caption and tagging support

**User Stories Foundation:**
- As a participant, I can upload photos to shared activities
- As a viewer, I can display a live photo gallery
- As an admin, I can moderate uploaded images
- As a system, I can filter inappropriate visual content

## Technical Infrastructure Features

### 14. Anonymous User Management
**Description:** Seamless participation without account creation or authentication.

**Key Components:**
- Temporary user session management
- Unique participant identification
- Optional nickname/display name support
- Session-based permissions

**User Stories Foundation:**
- As a participant, I can join sessions without creating accounts
- As a system, I can track participants within sessions uniquely
- As an admin, I can manage session access without user management overhead
- As a participant, I can optionally provide display names

### 15. Cross-Device Synchronization
**Description:** Consistent experience across mobile, tablet, and desktop devices.

**Key Components:**
- Responsive design for all interfaces
- Mobile-first participant experience
- Large screen optimized viewer displays
- Device capability detection and optimization

**User Stories Foundation:**
- As a participant, I can use any device to join and participate
- As a viewer, I can run sessions on various display sizes
- As an admin, I can manage sessions from desktop or mobile
- As a system, I can optimize experiences for different devices

### 16. Extensible Activity Plugin System
**Description:** Framework for adding new activity types without core system changes.

**Key Components:**
- Activity template definitions
- Plugin registration and loading
- Custom activity metadata schemas
- Activity-specific UI component system

**User Stories Foundation:**
- As a developer, I can create new activity types using templates
- As an admin, I can add custom activities to sessions
- As a system, I can load and validate new activity plugins
- As an organization, I can extend the platform for specific use cases

---

## Feature Prioritization Notes

**MVP Core (Phase 1):**
- Session Management ⏳ (Backend needed)
- Activity Framework ⏳ (Backend needed)
- Multi-Persona Interface System ✅ **COMPLETED**
- API Client Integration System ✅ **COMPLETED**
- Polling-Based Synchronization Engine ✅ **FRONTEND COMPLETE** (Backend integration ready)
- QR Code and Participant Onboarding ✅ **UI COMPLETE** (Backend integration ready)
- Live Polling System ✅ **FRONTEND FRAMEWORK COMPLETE** (Backend needed)
- Anonymous User Management ⏳ (Backend needed)
- Static Site Deployment ✅ **COMPLETED** (AWS S3 + CloudFront ready)

**Frontend Foundation Status:** ✅ **COMPLETE & PRODUCTION READY**
- React multi-persona interface fully implemented ✅
- SPA architecture optimized for static hosting ✅
- TanStack Query polling framework configured for SPA ✅
- Orval API client generation with type safety ✅
- Component architecture established ✅
- Testing framework (Vitest) operational ✅
- MSW mock infrastructure for comprehensive testing ✅
- Static build system ready for S3/CloudFront deployment ✅
- Zero additional frontend work needed for backend integration ✅

**Enhanced Engagement (Phase 2):**
- Planning Poker System
- Interactive Quiz/Trivia System
- Word Cloud Generator
- Live Reaction System

**Advanced Platform (Phase 3):**
- Content Moderation System
- Session Analytics and Reporting
- Photo Sharing Activity
- Extensible Activity Plugin System

**Infrastructure & Scale (Phase 4):**
- Cross-Device Synchronization enhancements
- Advanced analytics
- Enterprise features
- Performance optimizations

---

## Development and Deployment Features

### 17. GitHub Copilot Rules Integration
**Description:** Comprehensive AI-assisted development with project-specific rules and context.

**Key Components:**
- Project-specific Copilot instruction files (.copilot/instructions.md)
- Architecture guidelines and patterns
- Persona-specific UI development rules
- Activity framework implementation standards
- Tech stack and AWS deployment patterns

**User Stories Foundation:**
- As a developer, I can leverage AI assistance that understands our architecture
- As a team, we can maintain consistent code patterns across all features
- As a contributor, I can onboard quickly with AI-guided development
- As a project, we can ensure architectural decisions are consistently applied

### 18. Model Context Protocol (MCP) Integration
**Description:** Enhanced development workflow with GitHub integration for issue and story management.

**Key Components:**
- GitHub MCP server configuration
- Issue creation and management from development environment
- Story tracking and requirements traceability
- Automated workflow integration with VS Code

**User Stories Foundation:**
- As a developer, I can create and manage GitHub issues from my development environment
- As a team, we can maintain traceability from requirements to implementation
- As a project manager, I can track progress through integrated tooling
- As a contributor, I can follow standardized workflows for feature development

### 19. Infrastructure as Code (Terraform)
**Description:** Complete AWS infrastructure management through declarative configuration.

**Key Components:**
- Terraform modules for VPC, ECS, RDS, S3, CloudFront
- Environment-specific configurations (dev/staging/prod)
- Remote state management with S3 backend
- Automated deployment pipeline integration
- Resource naming conventions and tagging standards

**User Stories Foundation:**
- As a platform engineer, I can manage all infrastructure through code
- As a team, we can version control our infrastructure changes
- As a deployment system, I can ensure consistent environments across stages
- As a project, we can automate infrastructure provisioning and updates

### 20. Static Site Generation & Deployment ✅ **IMPLEMENTED**
**Description:** Single Page Application architecture optimized for AWS S3 static hosting with CloudFront CDN.

**Key Components:**
- **SPA Build System:** Vite-powered static asset generation ✅
- **Client-Side Routing:** TanStack Router for browser-based navigation ✅
- **Static Entry Point:** Standard HTML entry with JavaScript bootstrap ✅
- **CDN Optimization:** All assets suitable for aggressive CDN caching ✅
- **API Integration Ready:** Generated hooks compatible with backend services ✅
- **Build Pipeline:** `npm run build:spa` generates production-ready static assets ✅

**Technical Implementation:**
- **Framework:** Migrated from TanStack Start SSR to pure SPA architecture
- **Build Output:** Standard HTML, CSS, JS files deployable to any static hosting
- **Routing Strategy:** Client-side routing with fallback to index.html for deep links
- **State Management:** Browser-based persistence with API integration framework
- **Asset Optimization:** Vite rollup configuration for optimal bundle sizes

**Deployment Architecture:**
- **S3 Bucket:** Static website hosting with public read access
- **CloudFront:** Global CDN with optimized caching policies
- **Route 53:** DNS management for custom domain mapping
- **Build Pipeline:** Automated S3 sync with CloudFront cache invalidation

**User Stories Foundation:**
- As a deployment system, I can serve the application from static CDN infrastructure ✅
- As a global user, I can access the application with minimal latency from edge locations ✅
- As a developer, I can deploy frontend changes without server infrastructure ✅
- As a cost optimizer, I can serve unlimited traffic at minimal hosting costs ✅
- As a scaling system, I can handle traffic spikes through CDN infrastructure ✅

### 21. Development Orchestration (Makefile) ⏳ **IN PROGRESS**
**Description:** Unified development workflow management for full-stack application coordination.

**Key Components:**
- **Service Management:** `start-backend`, `start-frontend`, `start-all`
- **Lifecycle Control:** `stop-all`, `restart-all`, `status`
- **Testing Coordination:** `test-backend`, `test-frontend`, `test-all`
- **Development Tools:** `test-watch`, `test-coverage`
- **Process Management:** Background process handling and cleanup
- **Environment Setup:** Dependency validation and service health checks

**Enhanced Implementation Process:**
- AI-generated implementation plans with developer review capability
- Scope modification before execution begins
- Technical approach validation and alignment
- Effort estimation and retrospective tracking
- Plan documentation serving as implementation guide

**User Stories Foundation:**
- As a developer, I can start the entire application stack with a single command
- As a team member, I can run tests across all services consistently
- As a contributor, I can validate my environment setup before development
- As a developer, I can monitor service status and manage processes effectively
- As a team, we can coordinate development workflows across frontend and backend
- As a developer, I can review and refine implementation plans before execution

## Integration Points

Each feature is designed to integrate with the core session and activity framework, ensuring consistent user experience and data flow throughout the platform. The modular design allows for independent development and deployment of features while maintaining system cohesion.

The development workflow features ensure that team collaboration, AI assistance, and infrastructure management are seamlessly integrated into the development process, supporting rapid iteration and reliable deployment to AWS infrastructure.
