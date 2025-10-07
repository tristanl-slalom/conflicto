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

## Enhanced Workflow Steps

### 1. Pre-Implementation Phase (Specification Generation)

#### GitHub MCP Integration
- Use GitHub MCP server to fetch complete issue context
- Retrieve title, description, acceptance criteria, and labels
- Get dependencies, related issues, and linked PRs
- Analyze recent comments and implementation discussions

#### Issue Documentation Structure Creation
- Create `ai-docs/requirements/issues/issue-{number}/` folder
- Generate `issue-{number}_{title-slug}.spec.md` - Technical specification
- Generate `issue-{number}_{title-slug}.plan.md` - Implementation plan

#### Specification File Generation (`issue-X_title.spec.md`)
```markdown
# Technical Specification: [Issue Title]

**GitHub Issue:** [#X](link)
**Generated:** [timestamp]

## Problem Statement
[Extracted from issue description]

## Technical Requirements
[Derived technical requirements]

## API Specifications
[Endpoint definitions, request/response schemas]

## Data Models
[Database schemas, entity relationships]

## Interface Requirements
[UI/UX specifications if applicable]

## Integration Points
[External services, dependencies]

## Acceptance Criteria
[Technical acceptance criteria]

## Assumptions & Constraints
[Technical assumptions and limitations]
```

#### Plan File Generation (`issue-X_title.plan.md`)
```markdown
# Implementation Plan: [Issue Title]

**GitHub Issue:** [#X](link)
**Generated:** [timestamp]

## Implementation Strategy
[High-level approach]

## File Structure Changes
[New files to create, existing files to modify]

## Implementation Steps
1. [Step 1 with file changes]
2. [Step 2 with file changes]
3. [etc.]

## Testing Strategy
[Unit tests, integration tests to create]

## Deployment Considerations
[Migration scripts, environment changes]

## Risk Assessment
[Potential issues and mitigation strategies]

## Estimated Effort
[Time estimation and complexity assessment]
```

### 2. Developer Review Phase
- Command pauses and displays generated specification and plan files
- Developer reviews ai-docs/requirements/issue-X/ documentation
- Provides feedback or approval to proceed with implementation
- Allows modifications to spec/plan before code generation

### 3. Implementation Phase (After Approval)

#### Branch Management
- Auto-generate branch name: `feature/issue-{number}-{descriptive-slug}`
- Ensure main branch is current
- Create and push feature branch
- Switch to feature branch for implementation

#### Issue Analysis
- Categorize issue by labels (infrastructure/backend/frontend/activity)
- Identify Caja architecture requirements
- Determine multi-persona impact (admin/viewer/participant)
- Assess dependencies and potential blockers
- Reference approved specification and plan files during implementation

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

## Command Options

- `/conflictoIssue <number>` - Full workflow (spec → plan → review → implement)
- `/conflictoIssue <number> --spec-only` - Generate only specification file
- `/conflictoIssue <number> --plan-only` - Generate only implementation plan
- `/conflictoIssue <number> --implement` - Skip to implementation (if spec/plan exist)

## Expected Output Format

### Phase 1: Specification Generation
```
🔍 Fetching issue #{number} via GitHub MCP...
📋 Issue: "{issue-title}"
📄 Generated specification: ai-docs/requirements/issue-{number}/issue-{number}_{title-slug}.spec.md
📋 Generated plan: ai-docs/requirements/issue-{number}/issue-{number}_{title-slug}.plan.md

📚 Specification and implementation plan generated!

Please review:
- ai-docs/requirements/issue-{number}/issue-{number}_{title-slug}.spec.md
- ai-docs/requirements/issue-{number}/issue-{number}_{title-slug}.plan.md

Type 'proceed' to continue with implementation, or 'abort' to stop.
```

### Phase 2: Implementation (After Approval)
```
✅ Proceeding with implementation based on approved specification...
🌿 Created branch: feature/issue-{number}-{slug}
🏗️  Generated {file-count} files following specification
🧪 Added comprehensive test suite
📚 Updated documentation and API specs
✅ Implementation checklist ready with {criteria-count} acceptance criteria

Next steps:
1. Review generated code against specification requirements
2. Run test suite: npm test (frontend) or pytest (backend)
3. Validate acceptance criteria implementation
4. Create pull request when ready for review
```

## Benefits of Enhanced Workflow

1. **Better Planning:** Forces detailed thinking before coding
2. **Review Process:** Allows developer oversight of AI interpretation
3. **Documentation:** Creates searchable implementation history
4. **Consistency:** Ensures all implementations follow reviewed specifications
5. **Debugging:** Easier to trace implementation decisions back to plans
6. **Learning:** Developers can see AI's interpretation and planning process

This custom prompt enables efficient, MCP-powered issue implementation while maintaining consistency with Caja's architecture and development standards.
