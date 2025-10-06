# Caja - Live Event Engagement Platform

You are working on Caja, a modular platform for live event engagement at workplace events (town halls, team meetings, training sessions). The platform enables real-time interaction through personal devices while displaying results on shared screens.

## Quick Commands

### 🚀 Issue Commands (Always use GitHub MCP)
- **"do issue X"** → Fetch issue details via MCP, create feature branch, provide analysis
- **"implement issue X"** → Complete implementation with code generation, tests, and documentation
- **"/issue X"** → Slash command for complete issue implementation workflow

## Core Principles
- Extensible and modular architecture for easy addition of new activity types
- Mobile-first participant experience with large-screen viewer optimization
- Anonymous participation with no required user accounts
- Polling-based synchronization across all connected devices (not WebSockets for MVP)
- Session-based temporary user management

## Technology Stack

### Backend
- **Framework:** Python with FastAPI 
- **Testing:** Pytest for comprehensive test coverage
- **Deployment:** Amazon ECS (Elastic Container Service)
- **Real-time:** Polling-based updates (every 2-3 seconds)

### Frontend  
- **Framework:** React with TypeScript for type safety
- **Hosting:** Amazon S3 with CloudFront CDN
- **Styling:** Tailwind CSS for responsive design
- **Testing:** Jest/RTL for component testing

### Data Persistence
- **Primary Database:** Amazon RDS (PostgreSQL) for session data
- **Cache/Real-time State:** Redis for polling state management
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

## Copilot Command Rules

### "Do Issue {Number}" Command
**IMMEDIATE ACTION REQUIRED**: When user types "do issue X" or "work on issue X":

1. **Use MCP to fetch issue details** - No exceptions, always fetch from GitHub
2. **Auto-generate branch name**: `feature/issue-{number}-{slug}` from issue title
3. **Execute git commands** to create and push branch:
   ```bash
   git checkout main && git pull origin main
   git checkout -b feature/issue-{number}-{slug}
   git push -u origin feature/issue-{number}-{slug}
   ```
4. **Provide issue analysis** including requirements, architecture considerations, and next steps
5. **No confirmation needed** - Execute immediately

### "Implement Issue {Number}" Command
**COMPREHENSIVE IMPLEMENTATION**: When user types "implement issue X":

1. **Use MCP to fetch complete issue context** including dependencies and related PRs
2. **Create feature branch** if not already on one for this issue
3. **Analyze technical requirements** and break down into implementation tasks
4. **Generate code scaffolding** based on issue type (infrastructure/backend/frontend)
5. **Create initial files** with proper structure and boilerplate
6. **Add comprehensive tests** following Caja testing patterns
7. **Update documentation** as needed for the feature
8. **Provide implementation checklist** with acceptance criteria tracking

### "/issue {Number}" Slash Command
**PREFERRED METHOD**: When user types "/issue X":

Follow the complete workflow defined in [GitHub Custom Prompt](../../.github/copilot/issue-implementation.md):
1. **GitHub MCP integration** for issue context
2. **Automatic branch creation** with proper naming
3. **Code generation** based on issue labels and type
4. **Comprehensive testing** implementation
5. **Documentation updates** and checklists
6. **Team-specific guidance** based on issue category

This is now available as a repository-specific custom prompt via the `.github/copilot/` configuration.

## Code Standards
- Use TypeScript interfaces for all data structures
- Implement proper error handling with try-catch blocks
- Add comprehensive logging for debugging and CloudWatch
- Write unit tests for all business logic
- Use dependency injection for better testability
- Follow REST API conventions for HTTP endpoints
- Container-ready code with proper health checks
- Environment-specific configuration via environment variables

## Development Workflow

### Issue-Driven Development
**CRITICAL: Always use GitHub MCP to evaluate and work on issues.**

#### Quick Issue Workflow Command
When user says **"do issue {number}"** or **"work on issue {number}"**:

1. **IMMEDIATELY use MCP** to fetch the complete issue details:
   ```
   Use github-pull-request tools to get issue #{number} including:
   - Full title, description, and acceptance criteria
   - Labels, assignees, and current status
   - Dependencies and related issues
   ```

2. **Auto-generate feature branch name** from issue:
   ```
   Pattern: feature/issue-{number}-{descriptive-slug}
   - Extract key words from issue title
   - Convert to lowercase kebab-case
   - Limit to 50 characters total
   ```

3. **Create the branch immediately**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/issue-{number}-{slug}
   git push -u origin feature/issue-{number}-{slug}
   ```

4. **Provide issue analysis** covering:
   - Summary of requirements and acceptance criteria
   - Technical approach aligned with Caja architecture
   - Persona considerations (admin/viewer/participant)
   - Dependencies and potential blockers
   - Next steps for implementation

When starting any development work:
1. **Leverage MCP** to fetch complete issue context (title, description, acceptance criteria, dependencies)
2. **Create feature branch** using pattern: `feature/issue-{number}-{descriptive-slug}`
3. **Analyze requirements** against Caja architecture and multi-persona constraints
4. **Implement with proper tracking** using issue-linked commits and PRs

### Git Conventions
- Feature branches: `feature/issue-5-session-lifecycle-management`
- Commit messages: `feat(#5): add session creation API endpoint`
- PR titles: `[Issue #5] Feature - Session Management: Implement lifecycle API`

### Code Review Rules
- All PRs require review from at least one team member
- Run full test suite before merging
- Check mobile responsiveness for frontend changes
- Verify polling functionality for real-time features
- Validate Terraform plans for infrastructure changes
- Ensure issue acceptance criteria are fully met

### Environment Setup
- Use Docker for consistent development environments
- Environment variables for configuration
- Separate configs for development/staging/production
- Database migrations using Alembic
- Local development with Docker Compose

## Team Structure
- **Platform Engineering (Dom):** AWS infrastructure, Terraform, ECS deployment
- **Backend Development (Mauricio):** FastAPI application, database design, API endpoints  
- **Frontend Development (Joe):** React application, participant/viewer interfaces
- **Development Tooling (Dom):** GitHub MCP integration, VS Code configuration

## Related Documentation
- [Architecture & Data Models](./.copilot/architecture.md)
- [User Personas & UI Guidelines](./.copilot/personas.md)
- [Activity Framework](./.copilot/activities.md)
- [Implementation Standards](./.copilot/tech-stack.md)
- [GitHub MCP Integration](./.copilot/github-mcp.md)
- [Issue-Driven Development Workflow](./.copilot/issue-workflow.md)
- [GitHub Custom Prompts](../../.github/copilot/README.md)