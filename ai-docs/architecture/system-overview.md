# Caja System Architecture Overview

## Project Identity & Purpose

**Caja** is a modular platform for live event engagement at workplace events (town halls, team meetings, training sessions). The platform enables real-time interaction through personal devices while displaying results on shared screens.

## High-Level Architecture

### Monorepo Structure
```
conflicto/
├── backend/          # Python FastAPI application
│   ├── app/
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routes/      # API route handlers
│   │   ├── services/    # Business logic layer
│   │   ├── core/        # Configuration and logging
│   │   └── db/          # Database setup and models
│   ├── tests/           # Backend test suites
│   ├── migrations/      # Alembic database migrations
│   └── Dockerfile       # Container definition
├── frontend/         # React application (future)
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Route-based page components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── services/    # API communication
│   │   └── types/       # TypeScript type definitions
├── infrastructure/   # Terraform AWS resources
│   ├── modules/         # Reusable Terraform modules
│   └── environments/    # Environment-specific configs
└── ai-docs/          # AI-generated documentation
    ├── architecture/    # System design documentation
    ├── requirements/    # Issue specifications and plans
    └── transcripts/     # Meeting and discussion records
```

## Core Data Models

### Session
- **Purpose:** Container for a complete event with ordered activities
- **States:** draft → active → completed
- **Key Attributes:** name, status, admin_id, created_at
- **Relationships:** One-to-many with Activities and Participants

### Activity
- **Purpose:** Individual interactive element within a session
- **Types:** 'poll', 'poker', 'quiz', 'wordcloud'
- **States:** draft → published → active → expired
- **Key Attributes:** type, config (JSON), order, status
- **Relationships:** Belongs to Session, has many Responses

### Participant
- **Purpose:** Anonymous user participating in a session
- **Scope:** Session-scoped identification (no permanent accounts)
- **Key Attributes:** nickname, session_id, joined_at, last_activity
- **Relationships:** Belongs to Session, has many Responses

## System Components

### Backend Services (FastAPI)
- **Session Management:** CRUD operations, lifecycle management
- **Activity Framework:** Generic activity system with type-specific configurations
- **Participant Management:** Anonymous user handling, nickname validation
- **Real-time Polling:** State synchronization endpoints (2-3 second intervals)
- **Health Monitoring:** ECS-compatible health checks and metrics

### Frontend Interfaces (React - Future)
- **Admin Interface:** Session configuration, activity setup, content management
- **Viewer/Runner Interface:** Large screen display, QR codes, session control
- **Participant Interface:** Mobile-first activity interaction

### Infrastructure (AWS)
- **Application Hosting:** Amazon ECS with Application Load Balancer
- **Database:** Amazon RDS (PostgreSQL) with Multi-AZ deployment
- **Frontend Hosting:** Amazon S3 with CloudFront CDN
- **Container Registry:** Amazon ECR for Docker images
- **Infrastructure as Code:** Terraform modules for all AWS resources

## Communication Patterns

### Real-time Synchronization
- **Approach:** Polling-based updates (no WebSockets initially)
- **Frequency:** Client polls every 2-3 seconds for state changes
- **Benefits:** Simpler implementation, better error handling, easier debugging
- **Endpoints:** Optimized for incremental state updates

### Data Flow
1. **Admin creates session** → Session in draft state
2. **Admin opens session** → Session becomes active, QR code generated
3. **Participants scan QR** → Join session with nickname
4. **Activities progress** → State updates polled by all clients
5. **Participants respond** → Responses aggregated in real-time
6. **Session completes** → Summary generated, session archived

## Security & Access Control

### Anonymous Participation
- No user accounts or authentication required for participants
- Session-scoped participant identification via UUIDs
- Nickname-based display names with uniqueness validation

### Session Access Control
- Sessions accessible via QR code or direct URL
- Admin access through separate authentication (future enhancement)
- Session state controls participant capabilities

### Content Moderation
- Input validation and sanitization for all user content
- Content filtering for inappropriate material (future enhancement)
- Admin moderation capabilities for real-time content review

## Scalability Considerations

### Database Design
- Indexed queries for session and participant lookups
- Efficient polling endpoints to minimize database load
- Connection pooling for high-concurrent access
- Partitioning strategies for large-scale events

### Application Scaling
- Stateless FastAPI application design for horizontal scaling
- ECS auto-scaling based on CPU/memory metrics
- Database connection pooling and query optimization
- CDN caching for static assets and API responses

### Performance Targets
- Support 500+ concurrent participants per session
- Sub-second response times for state updates
- 99.9% uptime during active sessions
- Graceful degradation under high load

## Development Patterns

### Code Organization
- Service layer pattern for business logic
- Repository pattern for data access
- Dependency injection for testability
- Clear separation between API, business logic, and data layers

### Testing Strategy
- Unit tests for business logic (pytest)
- Integration tests for API endpoints
- Database tests with test fixtures
- Performance tests for concurrent load
- End-to-end tests for user workflows

### Deployment Pipeline
- GitHub Actions for CI/CD
- Automated testing and quality gates
- Terraform validation and planning
- Blue-green deployment for zero downtime
- Rollback procedures for failed deployments

This architecture supports the core requirements of live event engagement while providing a foundation for extensibility and scale.
