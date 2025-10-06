# GitHub Copilot Rules Implementation Plan

## Overview

This plan outlines how to translate the Caja app requirements and features into actionable GitHub Copilot rules that will guide AI-assisted development throughout the project lifecycle.

## Copilot Rules Structure

### Primary Rules File: `.copilot/instructions.md`

This will be the main instruction file that GitHub Copilot references for all code generation and suggestions.

### Supporting Context Files:
- `.copilot/architecture.md` - System architecture and design patterns
- `.copilot/personas.md` - User persona definitions and UX guidelines  
- `.copilot/activities.md` - Activity framework specifications
- `.copilot/tech-stack.md` - Technology choices and implementation standards

## Implementation Phases

### Phase 1: Core Project Rules (.copilot/instructions.md)

**Project Identity & Purpose:**
```markdown
# Caja - Live Event Engagement Platform

You are working on Caja, a modular platform for live event engagement at workplace events (town halls, team meetings, training sessions). The platform enables real-time interaction through personal devices while displaying results on shared screens.

## Core Principles
- Extensible and modular architecture for easy addition of new activity types
- Mobile-first participant experience with large-screen viewer optimization
- Anonymous participation with no required user accounts
- Real-time synchronization across all connected devices
- Session-based temporary user management
```

**Tech Stack Rules:**
```markdown
## Technology Stack

### Backend
- **Framework:** Python with FastAPI 
- **Testing:** Pytest for comprehensive test coverage
- **Deployment:** Amazon ECS (Elastic Container Service)
- **Real-time:** WebSocket connections for live updates

### Frontend  
- **Framework:** React with TypeScript for type safety
- **Hosting:** Amazon S3 with CloudFront CDN
- **Styling:** Tailwind CSS for responsive design
- **Testing:** Jest/RTL for component testing

### Data Persistence
- **Primary Database:** Amazon RDS (PostgreSQL) for session data
- **Cache/Real-time State:** Redis for WebSocket state management
- **File Storage:** Amazon S3 for media assets

### Infrastructure
- **Infrastructure as Code:** Terraform for all AWS resources
- **Container Registry:** Amazon ECR for Docker images
- **Load Balancing:** Application Load Balancer for ECS services
- **Monitoring:** CloudWatch for logging and metrics

### AWS Architecture
- **Networking:** VPC with public/private subnets
- **Security:** IAM roles, Security Groups, and NACLs
- **Secrets:** AWS Secrets Manager for database credentials
- **DNS:** Route 53 for domain management

## Code Standards
- Use TypeScript interfaces for all data structures
- Implement proper error handling with try-catch blocks
- Add comprehensive logging for debugging and CloudWatch
- Write unit tests for all business logic
- Use dependency injection for better testability
- Follow REST API conventions for HTTP endpoints
- Container-ready code with proper health checks
- Environment-specific configuration via environment variables
```

### Phase 2: Architecture Rules (.copilot/architecture.md)

**System Architecture:**
```markdown
## Monorepo Structure
```
caja/
├── backend/          # Python FastAPI application
│   ├── app/
│   │   ├── models/      # SQLAlchemy models
│   │   ├── api/         # API route handlers
│   │   ├── services/    # Business logic layer
│   │   ├── activities/  # Activity type implementations
│   │   └── websocket/   # Real-time communication
├── frontend/         # React application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Route-based page components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── services/    # API communication
│   │   └── types/       # TypeScript type definitions
└── shared/           # Shared types and utilities
```

**Data Models:**
```markdown
## Core Data Models

### Session
- id: UUID
- name: string
- status: 'draft' | 'active' | 'completed'  
- activities: Activity[]
- created_at: datetime
- admin_id: string

### Activity
- id: UUID
- session_id: UUID
- type: 'poll' | 'poker' | 'quiz' | 'wordcloud'
- config: JSON (activity-specific configuration)
- order: integer
- status: 'draft' | 'active' | 'expired'

### Participant
- id: UUID (session-scoped)
- session_id: UUID
- nickname: string
- joined_at: datetime
- last_activity: datetime
```

### Phase 3: User Experience Rules (.copilot/personas.md)

**Three-Persona System:**
```markdown
## User Personas & Interface Rules

### Admin Persona
- **Purpose:** Configure sessions and activities before launch
- **Interface:** Desktop-optimized with comprehensive controls
- **Key Actions:** Create sessions, configure activities, manage content
- **UI Rules:** 
  - Use form-based interfaces with validation
  - Provide preview modes for activities
  - Include draft/publish workflows
  - Show clear save states and error messages

### Viewer/Runner Persona  
- **Purpose:** Display session on large screen and control flow
- **Interface:** Large screen optimized with minimal controls
- **Key Actions:** Display activities, show live results, control progression
- **UI Rules:**
  - Large text and visual elements for visibility
  - Persistent small QR code in corner for joining
  - Prominent activity content with live result updates
  - Simple next/previous controls for session runner

### Participant Persona
- **Purpose:** Interact with activities on personal mobile device
- **Interface:** Mobile-first responsive design
- **Key Actions:** Join session, participate in activities, view personal results
- **UI Rules:**
  - Thumb-friendly touch targets (44px minimum)
  - Single-screen interactions with minimal scrolling
  - Clear call-to-action buttons
  - Real-time feedback for submissions
```

### Phase 4: Activity Framework Rules (.copilot/activities.md)

**Activity Development Pattern:**
```markdown
## Activity Framework Implementation

### Activity Base Class
Every activity type must implement:
- `ActivityConfig` interface for admin configuration
- `ParticipantView` component for mobile interaction  
- `ViewerDisplay` component for large screen display
- `ResultProcessor` for aggregating participant responses
- `StateManager` for activity lifecycle

### Activity States
All activities follow the same state machine:
1. **Draft:** Being configured by admin
2. **Active:** Accepting participant responses  
3. **Expired:** No longer accepting responses, showing results

### Real-time Updates
- Use WebSocket events for all state changes
- Emit events: 'activity:started', 'response:received', 'activity:completed'
- Handle reconnection gracefully with state recovery
```

### Phase 5: Implementation Guidelines (.copilot/tech-stack.md)

**Development Patterns:**
```markdown
## Implementation Standards

### API Development
- Use FastAPI dependency injection for services
- Implement request/response models with Pydantic
- Add OpenAPI documentation for all endpoints
- Use async/await for database operations
- Implement proper CORS for CloudFront integration
- Add health check endpoints for ECS service discovery
- Use structured logging for CloudWatch integration

### Frontend Development  
- Use React Context for session state management
- Implement custom hooks for WebSocket connections
- Use React Query for API state management
- Implement proper error boundaries
- Use Suspense for loading states
- Optimize for CloudFront caching with proper headers
- Implement responsive design for mobile-first approach

### Real-time Communication
- WebSocket connection per participant
- Broadcast updates to all session participants
- Handle connection drops with automatic reconnection
- Queue messages during disconnection periods
- Use Redis for WebSocket session state persistence

### AWS Deployment Patterns
- **ECS Services:** Auto-scaling based on CPU/memory metrics
- **RDS Configuration:** Multi-AZ for high availability
- **CloudFront:** Optimized caching rules for static assets
- **ALB Health Checks:** Custom health endpoints for service monitoring
- **Container Logging:** JSON structured logs to CloudWatch
- **Environment Management:** Separate environments (dev/staging/prod)

### Testing Strategy
- Unit tests for all business logic (Pytest for backend)
- Integration tests for API endpoints with test database
- Component tests for React components (Jest/RTL)
- End-to-end tests for critical user flows
- Load testing for real-time capabilities
- Infrastructure testing with Terraform validation
- Container testing in CI/CD pipeline before ECS deployment

### Security Standards
- **Database:** Encrypted RDS instances with rotation
- **Network:** Private subnets for backend services
- **Secrets:** AWS Secrets Manager for sensitive data
- **HTTPS:** SSL/TLS termination at CloudFront and ALB
- **Container Security:** Non-root user in Docker images
- **IAM:** Least-privilege access for all services
```

## Deployment Strategy

### Development Rules
```markdown
## Development Workflow

### Git Conventions
- Feature branches: `feature/session-management`
- Commit messages: "feat: add session creation API"
- PR titles: "[Feature] Session Management - API Implementation"

### Code Review Rules
- All PRs require review from at least one team member
- Run full test suite before merging
- Check mobile responsiveness for frontend changes
- Verify WebSocket functionality for real-time features
- Validate Terraform plans for infrastructure changes

### Environment Setup
- Use Docker for consistent development environments
- Environment variables for configuration
- Separate configs for development/staging/production
- Database migrations using Alembic
- Local development with Docker Compose

### Infrastructure as Code (Terraform)
- **Environment Separation:** Separate Terraform workspaces for dev/staging/prod
- **State Management:** Remote state in S3 with DynamoDB locking
- **Module Structure:** Reusable modules for VPC, ECS, RDS, CloudFront
- **Resource Naming:** Consistent naming conventions with environment prefixes
- **Security:** Terraform state encryption and access controls
- **CI/CD Integration:** Automated terraform plan/apply in deployment pipeline

### AWS Deployment Pipeline
- **Build Phase:** Docker image creation and ECR push
- **Test Phase:** Run tests against containerized application
- **Infrastructure Phase:** Terraform plan/apply for environment changes
- **Deploy Phase:** ECS service update with blue-green deployment
- **Validation Phase:** Health checks and smoke tests
- **Frontend Phase:** S3 sync and CloudFront invalidation
```

## Implementation Priorities

### Sprint 0 - Project Scaffolding (Week 1)
Focus Copilot rules on:
- Terraform AWS infrastructure setup (ECS, RDS, S3, CloudFront)
- FastAPI application structure with health checks
- React application setup with TanStack
- GitHub Actions CI/CD pipeline
- MCP integration for GitHub workflow
- Database schema and migrations

### Phase 1 - MVP Core (Weeks 2-5)
Focus Copilot rules on:
- Session CRUD operations with RDS persistence
- Polling-based synchronization implementation
- Simple poll activity type
- Three-persona UI framework
- QR code generation and participant onboarding

### Phase 2 - Enhanced Activities (Weeks 6-9)  
Expand Copilot rules for:
- Planning poker implementation
- Quiz/trivia system
- Word cloud generation
- Advanced polling features and result visualization

### Phase 3 - Advanced Features (Weeks 10-12)
Add Copilot rules for:
- Content moderation system
- Analytics and reporting
- Photo sharing activities
- Plugin architecture

## Validation & Testing

### Rule Effectiveness Metrics
- Code generation accuracy for domain concepts
- Consistency in following architectural patterns
- Proper implementation of persona-specific UIs
- Adherence to real-time communication patterns

### Iterative Improvement
- Weekly review of generated code quality
- Update rules based on common correction patterns
- Add new examples for complex scenarios
- Refine activity framework based on implementation learnings

---

## Next Steps

1. **Create `.copilot/` directory structure**
2. **Implement core instructions.md with project identity**
3. **Add architecture.md with system design patterns**  
4. **Define personas.md with UX guidelines**
5. **Create activities.md with framework specifications**
6. **Establish tech-stack.md with implementation standards**
7. **Test rules with initial code generation**
8. **Iterate based on results and team feedback**

This plan ensures GitHub Copilot understands the full context of the Caja platform and can generate code that aligns with the project's architectural decisions, user experience requirements, and technical standards.

## Team Integration and MCP Workflow

### Development Team Structure
- **Platform Engineering (Dom):** AWS infrastructure, Terraform, ECS deployment
- **Backend Development (Mauricio):** FastAPI application, database design, API endpoints  
- **Frontend Development (Joe):** React application, participant/viewer interfaces
- **Development Tooling (Dom):** GitHub MCP integration, VS Code configuration

### Model Context Protocol Integration
The GitHub MCP integration enables:
- Direct issue creation and management from VS Code
- Requirements traceability from features to implementation
- Automated story generation from refined requirements
- Consistent workflow patterns across team members

### Parallel Development Strategy
While Copilot rules are being implemented, team members can work independently on:
- Infrastructure setup (Terraform configurations)
- Application scaffolding (FastAPI and React boilerplate)
- Development environment configuration
- CI/CD pipeline establishment

This parallel approach ensures rapid progress while maintaining consistency through established rules and patterns.
```