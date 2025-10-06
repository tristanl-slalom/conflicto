# Caja - Live Event Engagement Platform

You are working on Caja, a modular platform for live event engagement at workplace events (town halls, team meetings, training sessions). The platform enables real-time interaction through personal devices while displaying results on shared screens.

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

### Git Conventions
- Feature branches: `feature/session-management`
- Commit messages: "feat: add session creation API"
- PR titles: "[Feature] Session Management - API Implementation"

### Code Review Rules
- All PRs require review from at least one team member
- Run full test suite before merging
- Check mobile responsiveness for frontend changes
- Verify polling functionality for real-time features
- Validate Terraform plans for infrastructure changes

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