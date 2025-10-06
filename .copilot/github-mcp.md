# GitHub MCP Server Integration

This project is integrated with the GitHub MCP (Model Context Protocol) server to enable seamless management of pull requests and issues directly from development tools and AI assistants.

## Overview

The GitHub MCP server provides the following capabilities:
- **Pull Request Management**: Create, read, update, and manage pull requests
- **Issue Management**: Create, read, update, and manage GitHub issues
- **Repository Operations**: Access repository information, files, and metadata
- **Code Review**: Facilitate code review processes through MCP tools

## Configuration

### MCP Server Setup

The MCP server configuration is located in `.mcp/server-config.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# GitHub Personal Access Token
GITHUB_TOKEN=your_github_personal_access_token_here
```

**Required GitHub Token Permissions:**
- `repo` - Full control of private repositories
- `public_repo` - Access to public repositories
- `pull_requests` - Access to pull requests
- `issues` - Access to issues
- `workflow` - Update GitHub Action workflows (if needed)

## Usage Examples

### Pull Request Management

#### Creating a Pull Request
```python
# Example workflow for creating a PR via MCP
# This would be handled by the MCP server integration
pr_data = {
    "title": "[Feature] Session Management - API Implementation",
    "body": "Implements core session management APIs for Caja platform",
    "head": "feature/session-management",
    "base": "main",
    "draft": False
}
```

#### Managing Pull Request Reviews
- Automatic assignment of reviewers based on team structure
- Integration with code review workflows
- Status checks and CI/CD integration

### Issue Management

#### Creating Issues
```python
# Example issue creation
issue_data = {
    "title": "Implement Redis polling for real-time updates",
    "body": "As part of the polling-based synchronization architecture, we need to implement Redis-backed polling for real-time state management.",
    "labels": ["enhancement", "backend", "redis"],
    "assignees": ["mauricio"],
    "milestone": "MVP Release"
}
```

#### Issue Templates
The following issue templates are recommended:

- **Bug Report**: For reporting bugs and issues
- **Feature Request**: For new feature proposals
- **Technical Debt**: For refactoring and improvements
- **Documentation**: For documentation updates

### Development Workflow Integration

#### Branch Management
- Feature branches: `feature/session-management`
- Bugfix branches: `bugfix/polling-timeout`
- Hotfix branches: `hotfix/security-patch`

#### Commit Conventions
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code formatting
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

#### PR Templates
Standard PR title format: `[Type] Component - Description`

Examples:
- `[Feature] Session Management - API Implementation`
- `[Fix] Polling Service - Timeout Handling`
- `[Docs] Architecture - Add Redis Documentation`

## Team Integration

### Role-Based Workflows

#### Platform Engineering (Dom)
- Infrastructure PRs and Terraform changes
- GitHub MCP server configuration and maintenance
- CI/CD pipeline management

#### Backend Development (Mauricio)
- FastAPI implementation PRs
- Database migration issues
- API endpoint documentation

#### Frontend Development (Joe)
- React component PRs
- Mobile responsiveness issues
- UI/UX improvements

### Automated Workflows

#### Issue Triage
- Automatic labeling based on content
- Assignment based on team expertise
- Priority setting based on keywords

#### Pull Request Automation
- Automatic reviewer assignment
- Status checks and CI integration
- Merge conflict notifications

## Best Practices

### Issue Management
1. Use descriptive titles and detailed descriptions
2. Apply appropriate labels for filtering and organization
3. Link related issues and PRs
4. Update issue status regularly
5. Close issues with clear resolution notes

### Pull Request Management
1. Keep PRs focused and atomic
2. Write clear descriptions with context
3. Include testing instructions
4. Request reviews from appropriate team members
5. Respond to feedback promptly

### Code Review Guidelines
1. Review for functionality, not just syntax
2. Check mobile responsiveness for frontend changes
3. Verify polling functionality for real-time features
4. Validate Terraform plans for infrastructure changes
5. Ensure comprehensive test coverage

## Monitoring and Analytics

The GitHub MCP integration provides insights into:
- PR cycle times and review efficiency
- Issue resolution rates
- Team collaboration patterns
- Code quality metrics

## Troubleshooting

### Common Issues

#### Authentication Errors
- Verify GitHub token permissions
- Check token expiration
- Ensure environment variables are set correctly

#### MCP Server Connection Issues
- Verify npx and Node.js installation
- Check network connectivity
- Review server logs for errors

#### Permission Denied Errors
- Verify repository access permissions
- Check team membership and roles
- Validate token scopes

### Support

For issues with the GitHub MCP integration:
1. Check the MCP server logs
2. Verify GitHub API rate limits
3. Consult the official MCP documentation
4. Contact the platform engineering team (Dom)