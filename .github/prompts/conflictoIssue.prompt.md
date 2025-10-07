---
mode: agent
description: "Fetch GitHub issue via MCP and implement complete solution with code generation"
---

# /conflictoIssue - Complete Issue Implementation Workflow

Implements a complete GitHub issue using the Model Context Protocol (MCP) server integration for the Caja live event engagement platform.

## Usage

```
conflictoIssue {issue-number}
```

## Examples

- `conflictoIssue 5` - Implement session lifecycle management
- `conflictoIssue 12` - Build word cloud generator activity
- `conflictoIssue 2` - Setup AWS infrastructure with Terraform

## Workflow Steps

### 1. GitHub MCP Integration
- Use GitHub MCP server to fetch complete issue context
- Retrieve title, description, acceptance criteria, and labels
- Get dependencies, related issues, and linked PRs
- Analyze recent comments and implementation discussions

### 2. Branch Management
- Auto-generate branch name: `featureconflictoIssue-{number}-{descriptive-slug}`
- Ensure main branch is current
- Create and push feature branch
- Switch to feature branch for implementation

### 3. Issue Analysis
- Categorize issue by labels (infrastructure/backend/frontend/activity)
- Identify Caja architecture requirements
- Determine multi-persona impact (admin/viewer/participant)
- Assess dependencies and potential blockers

### 4. Code Generation by Category

#### Infrastructure Issues (`feature:infrastructure`)
Generate:
- Terraform modules in `/infrastructure/modules/`
- GitHub Actions workflows in `.github/workflows/`
- Environment configurations for dev/staging/prod
- AWS resource definitions and security policies
- Monitoring and alerting configurations

#### Backend Issues (`feature:session-management`, `feature:activity-framework`)
Generate:
- FastAPI route handlers in `/backend/app/routes/`
- Pydantic request/response models in `/backend/app/models/`
- SQLAlchemy database models in `/backend/app/db/models/`
- Business logic services in `/backend/app/services/`
- Alembic database migrations
- Comprehensive pytest test suites

#### Frontend Issues (`feature:multi-persona-ui`, `feature:qr-onboarding`)
Generate:
- React components with TypeScript in `/frontend/src/components/`
- TanStack Query hooks in `/frontend/src/hooks/`
- Mobile-responsive layouts with Tailwind CSS
- Persona-specific routing and layouts
- Real-time polling integration components
- Jest/RTL component tests

#### Activity Issues (`feature:polling`, `feature:planning-poker`, etc.)
Generate:
- Activity plugin classes extending base framework
- Multi-persona activity components (admin/viewer/participant)
- Activity state management and lifecycle hooks
- Real-time synchronization integration
- Activity-specific configuration schemas

### 5. Test Implementation
Create comprehensive test coverage:
- Unit tests for business logic and utilities
- Integration tests for API endpoints and database operations
- Component tests for React elements and user interactions
- End-to-end tests for critical user workflows
- Performance tests for real-time polling mechanisms

### 6. Documentation Updates
Update project documentation:
- OpenAPI/Swagger specifications for new API endpoints
- Component documentation for UI changes and props
- Architecture decision records for framework modifications
- Deployment procedures for infrastructure changes
- Feature documentation and usage examples

### 7. Implementation Checklist
Provide detailed validation checklist:

**Functional Requirements:**
- [ ] All acceptance criteria implemented and verified
- [ ] Multi-persona support working (admin/viewer/participant)
- [ ] Session integration functioning correctly
- [ ] Polling-based synchronization implemented
- [ ] Mobile responsiveness confirmed for participant interfaces

**Technical Requirements:**
- [ ] Code follows Caja architecture patterns and conventions
- [ ] Comprehensive test coverage achieved (>80%)
- [ ] Proper error handling and structured logging
- [ ] Database migrations created and tested (if applicable)
- [ ] API documentation updated and accurate

**Quality Assurance:**
- [ ] All CI/CD pipeline checks passing
- [ ] Performance acceptable with 50+ concurrent participants
- [ ] Security considerations addressed and validated
- [ ] Accessibility requirements met (WCAG 2.1 AA)
- [ ] Cross-browser compatibility verified

## Caja Architecture Compliance

### Session-Centric Design
- All features integrate with session lifecycle (draft → active → completed)
- Session context maintained across all components
- Session recovery and state persistence supported

### Multi-Persona Architecture
- **Admin Interface:** Configuration and content management
- **Viewer Interface:** Large screen displays with QR codes and live results
- **Participant Interface:** Mobile-first interaction and activity engagement

### Polling-Based Synchronization
- 2-3 second polling intervals (no WebSockets for MVP)
- Optimistic updates with conflict resolution
- Graceful handling of network interruptions
- Local state caching for performance

### Activity Framework Integration
- New activities extend base activity template
- Plugin architecture support for extensibility
- Consistent state management across activity types
- Smooth transitions between activities in session flow

## Team-Specific Guidance

### Platform Engineering (Dom) - Infrastructure Focus
- Terraform validation and planning procedures
- AWS resource naming conventions and tagging
- Security and compliance requirement validation
- Monitoring, alerting, and observability setup
- CI/CD pipeline integration and deployment automation

### Backend Development (Mauricio) - API Focus
- FastAPI routing patterns and middleware integration
- Database design principles and migration strategies
- Real-time polling implementation and optimization
- API security, authentication, and rate limiting
- Service layer architecture and dependency injection

### Frontend Development (Joe) - UI Focus
- React component composition and reusability patterns
- Mobile-first responsive design and accessibility
- TanStack Query state management and caching
- Cross-browser compatibility and performance optimization
- User experience consistency across personas

## Error Handling

### MCP Server Unavailable
- Provide fallback workflow with manual GitHub issue review
- Create feature branch using provided issue number
- Generate basic scaffolding based on assumed issue type
- Request user input for missing issue context

### Issue Not Found
- Display clear error message with issue number verification
- Suggest checking issue number and repository access
- Provide link to GitHub issues page for reference

### Branch Conflicts
- Check if current branch matches target issue number
- Offer to switch to existing branch or create variant
- Provide conflict resolution guidance
- Maintain development continuity

## Expected Output Format

```
🔍 Fetching issue #{number} via GitHub MCP...
📋 Issue: "{issue-title}"
🌿 Created branch: feature/issue-{number}-{slug}
🏗️  Generated {file-count} files with boilerplate code
🧪 Added comprehensive test suite
📚 Updated documentation and API specs
✅ Implementation checklist ready with {criteria-count} acceptance criteria

Next steps:
1. Review generated code and customize for specific requirements
2. Run test suite: npm test (frontend) or pytest (backend)
3. Validate acceptance criteria implementation
4. Create pull request when ready for review
```

This custom prompt enables efficient, MCP-powered issue implementation while maintaining consistency with Caja's architecture and development standards.
