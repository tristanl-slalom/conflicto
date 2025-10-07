# Conflicto Makefile Documentation

This document provides comprehensive documentation for the Conflicto development Makefile, which serves as the central hub for all development operations.

## Overview

The Makefile provides unified commands for managing the full-stack Conflicto application, including:
- **Backend**: FastAPI application with Poetry dependency management
- **Frontend**: React+TypeScript application with Vite and npm/yarn
- **Process Management**: Background server management with PID tracking
- **Testing**: Comprehensive test execution with coverage reporting
- **Code Quality**: Formatting, linting, and type checking for both codebases

## Quick Start

```bash
# Initial setup
make setup

# Start all development servers
make start-all

# Run all tests
make test

# Check server status
make status

# Stop all servers
make stop-all
```

## Configuration Variables

The Makefile supports customization through environment variables:

```bash
# Server ports
BACKEND_PORT=8000     # FastAPI server port (default: 8000)
FRONTEND_PORT=3000    # React dev server port (default: 3000)

# Directory paths
BACKEND_DIR=backend   # Backend directory name
FRONTEND_DIR=frontend # Frontend directory name

# Tool preferences
NODE_PACKAGE_MANAGER=npm  # Package manager: npm or yarn
PYTHON_EXEC=python3       # Python executable name
```

### Usage Examples

```bash
# Use different ports
BACKEND_PORT=8080 FRONTEND_PORT=3001 make start-all

# Use yarn instead of npm
NODE_PACKAGE_MANAGER=yarn make install-frontend
```

## Command Reference

### Setup & Installation

| Command | Description | Example |
|---------|-------------|---------|
| `make setup` | Complete project setup | `make setup` |
| `make install` | Install all dependencies | `make install` |
| `make install-backend` | Install backend dependencies only | `make install-backend` |
| `make install-frontend` | Install frontend dependencies only | `make install-frontend` |

### Development Servers

| Command | Description | Ports | Process Tracking |
|---------|-------------|-------|------------------|
| `make start-backend` | Start FastAPI server | 8000 | ✅ PID tracked |
| `make start-frontend` | Start React server | 3000 | ✅ PID tracked |
| `make start-all` | Start both servers | 8000, 3000 | ✅ Both tracked |
| `make stop-all` | Stop all servers | - | ✅ Graceful shutdown |
| `make restart-all` | Restart all servers | - | ✅ Clean restart |
| `make status` | Show server status | - | ✅ Live status |

**Aliases:** `make dev`, `make start`, `make stop`, `make restart`

### Testing & Quality

| Command | Description | Coverage |
|---------|-------------|----------|
| `make test` | Run all tests | - |
| `make test-backend` | Run backend tests only | Optional |
| `make test-frontend` | Run frontend tests only | Optional |
| `make test-watch` | Interactive watch mode | - |
| `make test-coverage` | Full coverage report | ✅ HTML + Terminal |
| `make format` | Format all code | - |
| `make lint` | Lint all code | - |
| `make type-check` | Type checking | - |
| `make quality` | All quality checks | ✅ Full suite |

### Database Operations

| Command | Description | Requirements |
|---------|-------------|--------------|
| `make migrate` | Run database migrations | Backend running |
| `make migration MESSAGE="desc"` | Create new migration | MESSAGE required |
| `make reset-db` | Reset database ⚠️ | Confirmation |
| `make db-shell` | PostgreSQL shell | Backend running |

### Docker Operations

| Command | Description | Requirements |
|---------|-------------|--------------|
| `make docker-build` | Build Docker images | Docker installed |
| `make docker-run` | Run with Docker Compose | Docker Compose |
| `make docker-push REGISTRY=url` | Push to registry | REGISTRY variable |

### Utilities

| Command | Description | Scope |
|---------|-------------|-------|
| `make clean` | Clean cache and build files | All projects |
| `make env-info` | Show environment information | System + Projects |
| `make help` | Show all commands | - |

## Process Management

The Makefile includes robust process management for development servers:

### PID Tracking
- Process IDs are stored in `.dev-processes/` directory
- `backend.pid` - FastAPI server process
- `frontend.pid` - React dev server process

### Health Checking
- `make status` shows real-time server status
- Detects and cleans up stale PID files
- Validates processes are actually running

### Graceful Shutdown
- `SIGTERM` sent first for clean shutdown
- `SIGKILL` sent after 2-second timeout if needed
- PID files automatically cleaned up

### Port Management
- Automatic port availability checking
- Clear error messages for port conflicts
- Configurable ports via environment variables

## Error Handling

The Makefile includes comprehensive error handling:

### Directory Validation
```bash
❌ Backend directory 'backend' not found
❌ Frontend directory 'frontend' not found
```

### Dependency Checking
```bash
❌ Poetry not found. Please install Poetry first:
   curl -sSL https://install.python-poetry.org | python3 -

❌ Node.js not found. Please install Node.js first
```

### Port Conflicts
```bash
⚠️  Port 8000 is already in use
PID   USER     COMMAND
1234  user     python -m uvicorn
```

## Common Workflows

### Initial Development Setup
```bash
# Clone repository
git clone <repository-url>
cd conflicto

# Complete setup
make setup

# Start development
make start-all

# Verify everything is running
make status
```

### Daily Development Workflow
```bash
# Start your day
make start-all

# Run tests before committing
make test

# Format and lint code
make quality

# Stop servers when done
make stop-all
```

### Testing Workflow
```bash
# Run all tests
make test

# Watch mode for active development
make test-watch

# Full coverage report
make test-coverage

# Quality assurance
make quality
```

### Debugging Workflow
```bash
# Check what's running
make status

# View environment details
make env-info

# Clean up if issues occur
make clean
make stop-all
make start-all
```

## Integration with IDEs

### VS Code Integration

Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start All Servers",
      "type": "shell",
      "command": "make",
      "args": ["start-all"],
      "group": "build"
    },
    {
      "label": "Run All Tests",
      "type": "shell",
      "command": "make",
      "args": ["test"],
      "group": "test"
    },
    {
      "label": "Stop All Servers",
      "type": "shell",
      "command": "make",
      "args": ["stop-all"],
      "group": "build"
    }
  ]
}
```

### IntelliJ/PyCharm Integration

1. Open **Settings > Tools > External Tools**
2. Add new tool:
   - **Name**: Start Development Servers
   - **Program**: make
   - **Arguments**: start-all
   - **Working Directory**: $ProjectFileDir$

## Troubleshooting

### Common Issues

**Issue**: Port already in use
```bash
# Solution: Stop conflicting process or use different port
make stop-all
# OR
BACKEND_PORT=8080 make start-backend
```

**Issue**: Permission denied
```bash
# Solution: Check file permissions
chmod +x backend/setup.sh
```

**Issue**: Dependencies not installed
```bash
# Solution: Run installation
make install
# OR individually
make install-backend
make install-frontend
```

**Issue**: Stale processes
```bash
# Solution: Clean shutdown and restart
make stop-all
make clean
make start-all
```

### Performance Optimization

- Use `make test-watch` for faster feedback during development
- Run `make clean` periodically to remove accumulated cache files
- Use specific commands (`make test-backend`) when working on single component

### Cross-Platform Notes

**Windows (WSL)**:
- Ensure WSL2 is used for better performance
- Use Windows Terminal for better output formatting

**macOS**:
- Install GNU Make via Homebrew if needed: `brew install make`
- Use `gmake` if system make is too old

**Linux**:
- Should work out of the box with most distributions
- Ensure `lsof` is installed for port checking

## Contributing

When adding new Makefile targets:

1. Update the `help` target with appropriate descriptions
2. Add comprehensive error handling
3. Include progress feedback for long-running operations
4. Update this documentation
5. Test on multiple platforms

### Target Naming Conventions

- Use descriptive, hyphenated names: `start-backend`, `test-coverage`
- Group related targets with common prefixes: `test-*`, `format-*`, `lint-*`
- Provide aliases for convenience: `dev` → `start-all`
- Use consistent emoji prefixes in output messages

### Error Message Guidelines

- Start with ❌ for errors, ⚠️ for warnings
- Provide actionable remediation steps
- Include relevant context (file paths, commands)
- Keep messages concise but informative
