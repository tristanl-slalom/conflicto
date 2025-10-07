# Issue-Driven Development Workflow with GitHub MCP

## Overview

This document defines the automated workflow for issue evaluation and feature branch creation using the GitHub MCP server integration. Follow these rules to ensure consistent development practices and seamless issue tracking.

## Quick Command: "Do Issue {Number}"

### Primary Workflow Command
When a user says **"do issue {number}"** or **"work on issue {number}"**, Copilot should:

1. **Immediately fetch issue via MCP**
2. **Generate appropriate branch name**
3. **Create and push the feature branch**
4. **Provide comprehensive issue analysis**

### Example Interaction:
```
User: "do issue 5"

Copilot Response:
1. Uses MCP to fetch issue #5 details
2. Creates branch: feature/issue-5-session-lifecycle-management
3. Provides analysis of requirements and next steps
```

## Issue Evaluation Rules

### When starting work on any GitHub issue:

1. **Leverage MCP to fetch comprehensive issue context:**
   ```
   Use GitHub MCP to retrieve:
   - Issue title, description, and acceptance criteria
   - Linked issues, dependencies, and related PRs
   - Issue labels, assignees, and milestone information
   - Recent comments and discussion context
   - Current project status and priority
   ```

2. **Analyze issue scope and requirements:**
   - Break down acceptance criteria into actionable tasks
   - Identify dependencies on other issues or features
   - Estimate complexity based on feature labels and description
   - Determine if issue needs further clarification or refinement

3. **Validate technical approach:**
   - Ensure proposed solution aligns with Caja architecture
   - Check compatibility with existing tech stack and patterns
   - Verify approach supports the three-persona system (admin/viewer/participant)
   - Confirm solution maintains polling-based synchronization architecture

## Automatic Branch Creation Rules

### Branch Naming Convention

Create feature branches using this exact pattern:
```
feature/issue-{issue-number}-{descriptive-slug}
```

Examples:
- `feature/issue-5-session-lifecycle-management`
- `feature/issue-9-live-polling-system`
- `feature/issue-14-cicd-pipeline-setup`

### Branch Creation Process

1. **Before creating any branch:**
   ```bash
   # Ensure you're on main and up to date
   git checkout main
   git pull origin main
   ```

2. **Create feature branch with MCP context:**
   ```bash
   # Create branch using issue information from MCP
   git checkout -b feature/issue-{number}-{slug}
   git push -u origin feature/issue-{number}-{slug}
   ```

3. **Update issue status:**
   - Move issue to "In Progress" if using project boards
   - Add "status:in-progress" label if not using boards
   - Assign yourself to the issue if not already assigned

### Branch Structure by Feature Type

#### Infrastructure Issues (feature:infrastructure)
```
feature/issue-{n}-{infrastructure-component}
Examples:
- feature/issue-2-aws-terraform-setup
- feature/issue-14-cicd-github-actions
- feature/issue-19-monitoring-observability
```

#### Backend API Issues (feature:session-management, feature:activity-framework)
```
feature/issue-{n}-{api-component}
Examples:
- feature/issue-3-fastapi-backend-foundation
- feature/issue-5-session-lifecycle-management
- feature/issue-7-activity-framework
```

#### Frontend UI Issues (feature:multi-persona-ui, feature:qr-onboarding)
```
feature/issue-{n}-{ui-component}
Examples:
- feature/issue-4-react-multi-persona-ui
- feature/issue-6-qr-participant-onboarding
```

#### Activity Type Issues (feature:polling, feature:planning-poker, etc.)
```
feature/issue-{n}-{activity-type}
Examples:
- feature/issue-9-live-polling-system
- feature/issue-10-planning-poker-activity
- feature/issue-11-interactive-trivia-system
```

## Development Workflow Integration

### Copilot Behavior Rules

**When user requests "do issue {number}" or "work on issue {number}":**

1. **STEP 1: Fetch Issue Data**
   - Use github-pull-request MCP tools to retrieve complete issue details
   - Get title, description, acceptance criteria, labels, assignees
   - Check for dependencies and related issues

2. **STEP 2: Generate Branch Name**
   ```
   Format: feature/issue-{number}-{descriptive-slug}
   Process:
   - Take issue title
   - Extract 3-5 key descriptive words
   - Convert to lowercase
   - Replace spaces/special chars with hyphens
   - Limit total length to 50 characters
   ```

3. **STEP 3: Create Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b {generated-branch-name}
   git push -u origin {generated-branch-name}
   ```

4. **STEP 4: Analyze and Guide**
   - Summarize issue requirements
   - Identify Caja architecture considerations
   - Note persona-specific requirements
   - Highlight dependencies or blockers
   - Suggest implementation approach
   - Provide next steps

**Never ask for confirmation - execute immediately when user says "do issue X"**

## Comprehensive Implementation Command: "Implement Issue {Number}"

**When user requests "implement issue {number}":**

1. **STEP 1: Fetch Complete Context via MCP**
   - Get issue details, acceptance criteria, and comments
   - Check for linked issues, dependencies, and blocking relationships
   - Analyze related PRs and previous implementation attempts
   - Review labels to determine feature category and complexity

2. **STEP 2: Branch Management**
   - Check if already on correct feature branch for this issue
   - If not, create branch using "do issue" workflow
   - Ensure branch is up to date with main

3. **STEP 3: Technical Analysis & Planning**
   - Determine implementation approach based on issue labels:
     - `feature:infrastructure` → Terraform, AWS resources, CI/CD
     - `feature:session-management` → FastAPI endpoints, database models
     - `feature:multi-persona-ui` → React components, routing, state management
     - `feature:activity-framework` → Plugin architecture, activity templates
     - `feature:polling` → Real-time sync, WebSocket alternatives
   - Identify required files and directory structure
   - Plan database migrations if needed
   - Consider multi-persona impact (admin/viewer/participant)

4. **STEP 4: Code Generation & Scaffolding**
   Based on issue type, create appropriate boilerplate:

   **Infrastructure Issues:**
   ```
   - Terraform module files (.tf)
   - GitHub Actions workflows (.yml)
   - Docker configurations
   - AWS resource definitions
   ```

   **Backend Issues:**
   ```
   - FastAPI route handlers
   - Pydantic models and schemas
   - Database models (SQLAlchemy)
   - Alembic migrations
   - Service layer classes
   ```

   **Frontend Issues:**
   ```
   - React components with TypeScript
   - TanStack Query hooks
   - Tailwind CSS styling
   - Mobile-responsive layouts
   - Route definitions
   ```

   **Activity Framework Issues:**
   ```
   - Activity template classes
   - Plugin registration code
   - UI component variants
   - State management logic
   ```

5. **STEP 5: Test Implementation**
   - Generate unit tests for business logic
   - Create integration tests for APIs
   - Add component tests for React elements
   - Include e2e tests for critical user flows
   - Follow pytest patterns for backend, Jest/RTL for frontend

6. **STEP 6: Documentation Updates**
   - Update API documentation if adding endpoints
   - Add component documentation for UI changes
   - Update architecture docs for framework changes
   - Include deployment notes for infrastructure changes

7. **STEP 7: Implementation Checklist**
   - Create detailed checklist mapping to acceptance criteria
   - Include testing requirements
   - Add code review checkpoints
   - Note deployment considerations
   - Track persona-specific validation needs

### Implementation Templates by Issue Type

#### Infrastructure Implementation Template
```typescript
// For feature:infrastructure issues
1. Create Terraform modules in /infrastructure/
2. Add GitHub Actions in .github/workflows/
3. Update environment configurations
4. Add monitoring and alerting
5. Document deployment procedures
```

#### Backend Implementation Template
```python
# For backend issues (session-management, activity-framework)
1. Create FastAPI routes in /backend/app/routes/
2. Add Pydantic models in /backend/app/models/
3. Create database models in /backend/app/db/models/
4. Add business logic in /backend/app/services/
5. Create Alembic migration
6. Add comprehensive pytest tests
```

#### Frontend Implementation Template
```tsx
// For frontend issues (multi-persona-ui, polling, activities)
1. Create React components in /frontend/src/components/
2. Add TanStack Query hooks in /frontend/src/hooks/
3. Create persona-specific layouts
4. Add mobile-responsive styling
5. Implement real-time polling integration
6. Add Jest/RTL component tests
```

**Never ask for confirmation - execute immediately when user says "implement issue X"**

### Issue Analysis Prompt Template

When starting work on an issue, use this template to leverage MCP:

```
Analyze GitHub issue #{issue-number} using MCP:

1. Fetch complete issue context including:
   - Full description and acceptance criteria
   - Related issues and dependencies
   - Current labels and priority status
   - Recent activity and comments

2. Create feature branch following naming convention:
   feature/issue-{number}-{descriptive-slug}

3. Evaluate technical approach considering:
   - Caja architecture patterns (session management, activity framework)
   - Multi-persona UI requirements (admin/viewer/participant)
   - Polling-based synchronization constraints
   - AWS infrastructure and deployment requirements

4. Identify dependencies and blockers:
   - Issues that must be completed first
   - Infrastructure requirements
   - External integrations needed

5. Create implementation plan with specific tasks
```

### Commit Message Integration

Link commits to issues using conventional format:
```
{type}(#{issue-number}): {description}

Examples:
feat(#5): implement session creation API endpoint
fix(#8): resolve polling timeout in real-time sync
docs(#21): add session management API documentation
test(#9): add unit tests for polling system
```

### Pull Request Creation Rules

1. **PR Title Format:**
   ```
   [Issue #{number}] {Feature/Fix} - {Component}: {Brief Description}

   Examples:
   [Issue #5] Feature - Session Management: Implement lifecycle API
   [Issue #14] Infrastructure - CI/CD: Add GitHub Actions pipeline
   [Issue #9] Feature - Polling System: Real-time synchronization
   ```

2. **PR Description Template:**
   ```markdown
   ## Related Issue
   Closes #{issue-number}

   ## Changes Made
   - [ ] List specific changes
   - [ ] Include acceptance criteria completed
   - [ ] Note any deviations from original plan

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests verified
   - [ ] Manual testing completed

   ## MCP Context
   {Include relevant context from issue analysis}

   ## Deployment Notes
   {Any infrastructure or deployment considerations}
   ```

### Quality Gates

Before marking issue as complete:

1. **Code Quality:**
   - All acceptance criteria met
   - Tests pass locally and in CI
   - Code follows Caja architecture patterns
   - Proper error handling implemented

2. **Feature Integration:**
   - Works within session framework
   - Supports all three personas appropriately
   - Maintains polling-based synchronization
   - Mobile-responsive (for participant interfaces)

3. **Documentation:**
   - API endpoints documented (if backend)
   - Component usage documented (if frontend)
   - Architecture decisions recorded
   - Deployment procedures updated (if infrastructure)

## MCP Server Commands for Issue Management

### Common MCP Queries

```javascript
// Fetch issue details
github-pull-request_openPullRequest()
github-pull-request_activePullRequest()

// Create branches based on issue analysis
// (This would be handled through git commands after MCP analysis)

// Update issue status
// (Handle through GitHub API via MCP)
```

### Issue Status Tracking

Use MCP to maintain issue lifecycle:

1. **Analysis Phase:**
   - Fetch issue details and requirements
   - Identify dependencies and blockers
   - Create feature branch

2. **Development Phase:**
   - Regular commits with issue references
   - Update issue with progress comments
   - Link related issues as needed

3. **Review Phase:**
   - Create PR with proper issue linking
   - Request appropriate reviewers based on labels
   - Address feedback and update issue

4. **Completion Phase:**
   - Merge PR to close issue automatically
   - Update project status
   - Archive branch after successful deployment

## Error Handling and Edge Cases

### If MCP Server is Unavailable:
- Fall back to manual issue review on GitHub
- Still follow branch naming conventions
- Include issue context in PR description manually

### For Complex Issues:
- Break into smaller sub-issues if needed
- Create tracking issue for epic coordination
- Use draft PRs for work-in-progress coordination

### For Dependencies:
- Block development until dependencies resolved
- Use GitHub's dependency tracking features
- Coordinate with team members on blocking issues

## Caja-Specific Implementation Patterns

### Architecture Considerations for Implementation

**Session-Centric Design:**
- All features must integrate with session lifecycle (draft → active → completed)
- Maintain session context across all components
- Support session recovery and state persistence

**Multi-Persona Requirements:**
- Admin interface: Configuration and management focused
- Viewer interface: Large screen display with QR codes and live results
- Participant interface: Mobile-first interaction and activity engagement

**Polling-Based Synchronization:**
- Use 2-3 second polling intervals instead of WebSockets
- Implement optimistic updates with conflict resolution
- Handle network interruptions gracefully
- Cache state locally for performance

**Activity Framework Integration:**
- New activities must extend base activity template
- Support plugin architecture for extensibility
- Maintain consistent state management across activity types
- Enable smooth transitions between activities in session flow

### Implementation Validation Checklist

Before marking implementation complete, verify:

**Functional Requirements:**
- [ ] All acceptance criteria are met
- [ ] Works across all three personas appropriately
- [ ] Integrates with session management system
- [ ] Supports polling-based real-time updates
- [ ] Mobile responsive (for participant interfaces)

**Technical Requirements:**
- [ ] Follows Caja architecture patterns
- [ ] Includes comprehensive test coverage
- [ ] Proper error handling and logging
- [ ] Database migrations (if applicable)
- [ ] API documentation updated (if applicable)

**Quality Assurance:**
- [ ] Code passes all CI/CD checks
- [ ] Performance acceptable with 50+ participants
- [ ] Security considerations addressed
- [ ] Accessibility requirements met
- [ ] Cross-browser compatibility verified

## Team Integration

### Role-Specific Workflows:

#### Platform Engineering (Dom):
- Focus on `feature:infrastructure` labeled issues
- Ensure Terraform validation before merging
- Coordinate deployment and AWS resource changes

#### Backend Development (Mauricio):
- Handle `feature:session-management`, `feature:activity-framework` issues
- Ensure FastAPI patterns and database migrations
- Coordinate with frontend on API contracts

#### Frontend Development (Joe):
- Work on `feature:multi-persona-ui`, activity-specific UI issues
- Ensure mobile responsiveness and accessibility
- Coordinate with backend on real-time polling integration

## Example Implementation Workflows

### Example 1: "implement issue 5" (Session Management)
```
1. MCP fetches issue #5: "Implement Session Lifecycle Management"
2. Creates branch: feature/issue-5-session-lifecycle-management
3. Generates:
   - /backend/app/routes/sessions.py (FastAPI endpoints)
   - /backend/app/models/session.py (Pydantic schemas)
   - /backend/app/db/models/session.py (SQLAlchemy models)
   - /backend/app/services/session_service.py (business logic)
   - /backend/tests/test_sessions.py (pytest tests)
   - Alembic migration for session tables
4. Provides implementation checklist with acceptance criteria
```

### Example 2: "implement issue 9" (Live Polling System)
```
1. MCP fetches issue #9: "Build Live Polling Activity System"
2. Ensures on correct branch or creates one
3. Generates:
   - /backend/app/activities/polling.py (activity implementation)
   - /frontend/src/components/activities/Polling/ (React components)
   - /frontend/src/hooks/usePollingActivity.ts (TanStack Query)
   - Real-time polling integration code
   - Mobile-responsive participant interface
   - Large-screen viewer display
   - Comprehensive test suites
4. Updates activity framework registration
5. Provides persona-specific testing checklist
```

### Example 3: "implement issue 2" (AWS Infrastructure)
```
1. MCP fetches issue #2: "Setup AWS Infrastructure with Terraform"
2. Creates infrastructure branch
3. Generates:
   - /infrastructure/modules/ (Terraform modules)
   - /infrastructure/environments/ (dev/staging/prod configs)
   - /.github/workflows/infrastructure.yml (CI/CD pipeline)
   - /infrastructure/monitoring.tf (CloudWatch setup)
   - /infrastructure/security.tf (IAM, Security Groups)
4. Provides infrastructure deployment checklist
5. Includes validation and rollback procedures
```

This workflow ensures that every piece of development work is:
- Directly tied to a GitHub issue with clear requirements
- Properly branched and tracked through the development lifecycle
- Integrated with our MCP server for seamless issue management
- Aligned with Caja's architecture and team structure
- Implemented with appropriate scaffolding and boilerplate code
- Validated against Caja-specific patterns and requirements
