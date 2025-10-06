# Copilot Slash Commands for Caja Development

## /issue {number} - Complete Issue Implementation

**Purpose:** Fetch issue details via GitHub MCP and implement the complete solution with code generation, testing, and documentation.

### Command Syntax
```
/issue 5
/issue 12
/issue 2
```

### Slash Command Behavior

When `/issue {number}` is invoked, execute the following workflow:

#### Step 1: GitHub MCP Integration
```
REQUIRED: Use GitHub MCP server to fetch complete issue context
- Issue title, description, and acceptance criteria
- Labels, assignees, current status, and priority
- Dependencies, related issues, and linked PRs
- Recent comments and implementation discussions
```

#### Step 2: Branch Management
```
Auto-generate branch name: feature/issue-{number}-{slug}
Where {slug} is derived from issue title:
- Extract 3-5 key descriptive words
- Convert to lowercase kebab-case
- Limit to 50 characters total

Execute git commands:
git checkout main
git pull origin main
git checkout -b feature/issue-{number}-{slug}
git push -u origin feature/issue-{number}-{slug}
```

#### Step 3: Issue Analysis & Planning
```
Analyze issue based on labels and provide:
- Technical requirements summary
- Architecture considerations for Caja platform
- Multi-persona impact (admin/viewer/participant)
- Dependencies and potential blockers
- Implementation approach recommendation
```

#### Step 4: Code Generation by Issue Type

**Infrastructure Issues (feature:infrastructure):**
```
Generate:
- Terraform modules in /infrastructure/modules/
- GitHub Actions workflows in .github/workflows/
- Environment configurations
- AWS resource definitions
- Monitoring and alerting setup
- Security and IAM configurations
```

**Backend Issues (feature:session-management, feature:activity-framework):**
```
Generate:
- FastAPI route handlers in /backend/app/routes/
- Pydantic models in /backend/app/models/
- SQLAlchemy models in /backend/app/db/models/
- Service layer classes in /backend/app/services/
- Alembic database migrations
- Pytest test suites in /backend/tests/
```

**Frontend Issues (feature:multi-persona-ui, feature:qr-onboarding):**
```
Generate:
- React components with TypeScript in /frontend/src/components/
- TanStack Query hooks in /frontend/src/hooks/
- Mobile-responsive layouts with Tailwind CSS
- Persona-specific interfaces (admin/viewer/participant)
- Real-time polling integration
- Jest/RTL component tests in /frontend/src/tests/
```

**Activity Issues (feature:polling, feature:planning-poker, etc.):**
```
Generate:
- Activity plugin classes extending base template
- React activity components for all personas
- State management for activity lifecycle
- Real-time synchronization logic
- Activity-specific tests and documentation
```

#### Step 5: Test Implementation
```
Generate comprehensive test suites:
- Unit tests for business logic
- Integration tests for API endpoints
- Component tests for React elements
- E2E tests for critical user flows
- Performance tests for polling mechanisms
```

#### Step 6: Documentation Updates
```
Update relevant documentation:
- OpenAPI/Swagger specs for new endpoints
- Component documentation for UI changes
- Architecture decision records for framework changes
- Deployment procedures for infrastructure changes
- README updates for new features
```

#### Step 7: Implementation Checklist
```
Provide detailed checklist mapping to acceptance criteria:
✅ Functional Requirements
- [ ] All acceptance criteria implemented
- [ ] Multi-persona support verified
- [ ] Session integration working
- [ ] Polling-based sync implemented
- [ ] Mobile responsiveness confirmed

✅ Technical Requirements  
- [ ] Code follows Caja architecture patterns
- [ ] Comprehensive test coverage achieved
- [ ] Error handling and logging added
- [ ] Database migrations created (if needed)
- [ ] API documentation updated (if applicable)

✅ Quality Assurance
- [ ] CI/CD checks passing
- [ ] Performance acceptable with 50+ participants
- [ ] Security considerations addressed
- [ ] Accessibility requirements met
- [ ] Cross-browser compatibility verified
```

### Example Slash Command Execution

```
User types: /issue 5

Expected Response:
1. "Fetching issue #5 details via GitHub MCP..."
2. "Issue: Implement Session Lifecycle Management"
3. "Creating branch: feature/issue-5-session-lifecycle-management"
4. "Generated FastAPI endpoints, models, services, and tests"
5. "Created database migration for session tables"
6. "Implementation checklist provided with 12 acceptance criteria"
```

### Caja-Specific Implementation Rules

**Session-Centric Design:**
- All features must integrate with session lifecycle states
- Maintain session context across components
- Support session recovery and persistence

**Multi-Persona Architecture:**
- Admin: Configuration and management interfaces
- Viewer: Large screen displays with QR codes and results
- Participant: Mobile-first interaction and engagement

**Polling-Based Synchronization:**
- Use 2-3 second polling intervals (no WebSockets for MVP)
- Implement optimistic updates with conflict resolution
- Handle network interruptions gracefully

**Activity Framework Integration:**
- New activities extend base activity template
- Support plugin architecture for extensibility
- Maintain consistent state management
- Enable smooth activity transitions

### Error Handling

If MCP server unavailable:
```
Fallback behavior:
1. Prompt user to check GitHub issue manually
2. Still create feature branch using provided issue number
3. Generate basic scaffolding based on assumed issue type
4. Request user to provide issue details for proper implementation
```

If issue doesn't exist:
```
Error response:
"Issue #{number} not found in repository. Please verify issue number and try again."
```

If branch already exists:
```
Branch conflict resolution:
1. Check if current branch matches issue number
2. If yes, continue with implementation
3. If no, prompt user to resolve branch conflict
4. Offer to switch to existing branch or create new variant
```

### Team-Specific Guidance

Based on issue labels, provide role-specific guidance:

**Platform Engineering (Dom) - Infrastructure Issues:**
```
Additional considerations:
- Terraform validation and planning
- AWS resource naming conventions
- Security and compliance requirements
- Monitoring and alerting setup
- CI/CD pipeline integration
```

**Backend Development (Mauricio) - API Issues:**
```
Additional considerations:
- FastAPI routing and middleware patterns
- Database design and migration strategies
- Real-time polling implementation
- API security and rate limiting
- Service layer architecture
```

**Frontend Development (Joe) - UI Issues:**
```
Additional considerations:
- React component composition patterns
- Mobile-first responsive design
- TanStack Query state management
- Accessibility and usability requirements
- Cross-browser compatibility testing
```

This slash command system provides a single, powerful interface for complete issue implementation while leveraging the GitHub MCP server for accurate, context-aware development workflows.