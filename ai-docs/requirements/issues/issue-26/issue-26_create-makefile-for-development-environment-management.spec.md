# Technical Specification: Create Makefile for Development Environment Management

**GitHub Issue:** [#26](https://github.com/tristanl-slalom/conflicto/issues/26)
**Generated:** October 7, 2025

## Problem Statement

The Caja platform development workflow currently lacks unified tooling for managing development servers, running tests, and handling common development tasks. Developers must manually navigate between backend and frontend directories, remember various command patterns, and manage multiple processes independently, leading to inconsistent development practices and reduced productivity.

## Technical Requirements

### Core Development Commands
- **Server Management:** Unified commands to start/stop/restart backend and frontend servers
- **Test Execution:** Consolidated test running for both codebases with coverage reporting
- **Dependency Management:** Single-command installation for all project dependencies
- **Code Quality:** Integrated linting and formatting for both backend and frontend
- **Environment Setup:** Automated initial development environment configuration

### Backend Integration (FastAPI)
- Integration with Poetry for dependency management
- FastAPI development server management (uvicorn)
- Pytest execution with coverage reporting
- Black/Flake8 code formatting and linting
- Database migration support

### Frontend Integration (React/TypeScript)
- Node.js package management (npm/yarn)
- React development server management (Vite)
- Jest/RTL test execution
- ESLint/Prettier code quality tools
- Build artifact management

## API Specifications

### Makefile Target Interface
```makefile
# Server Management Targets
start-backend:        # Start FastAPI server on port 8000
start-frontend:       # Start React server on port 3000
start-all:           # Start both servers in background with PID tracking
stop-all:            # Gracefully stop all tracked processes
restart-all:         # Sequential stop and start of all services
status:              # Display status of running development servers

# Testing Targets
test-backend:        # Run pytest with coverage in backend/
test-frontend:       # Run Jest tests in frontend/
test-all:           # Execute all test suites sequentially
test-watch:         # Run tests in watch mode for active development
test-coverage:      # Generate comprehensive coverage reports

# Development Utilities
install:            # Install backend and frontend dependencies
install-backend:    # Install Python dependencies via Poetry
install-frontend:   # Install Node.js dependencies via npm/yarn
lint:              # Run all linting tools
lint-backend:      # Run Black, Flake8, and mypy on backend code
lint-frontend:     # Run ESLint and type checking on frontend code
format:            # Auto-format all code
format-backend:    # Format Python code with Black
format-frontend:   # Format TypeScript/JavaScript with Prettier
clean:             # Remove build artifacts, cache files, and temporary files
setup:             # Complete initial development environment setup
help:              # Display all available targets with descriptions
```

## Data Models

### Process Tracking Schema
```bash
# PID file structure for background process management
.dev-processes/
├── backend.pid      # FastAPI server process ID
├── frontend.pid     # React dev server process ID
└── processes.log    # Process startup/shutdown log
```

### Configuration Variables
```makefile
# Configurable environment variables
BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 3000
BACKEND_DIR = backend
FRONTEND_DIR = frontend
PYTHON_EXEC ?= python3
NODE_PACKAGE_MANAGER ?= npm
TEST_COVERAGE_THRESHOLD = 80
```

## Interface Requirements

### Command Line Interface
- All targets must provide clear, actionable output
- Error messages should include suggested remediation steps
- Success messages should include relevant URLs and status information
- Progress indicators for long-running operations (installation, tests)

### Terminal Output Format
```bash
# Success Example
✅ Backend server started successfully
   URL: http://localhost:8000
   PID: 12345
   Logs: tail -f backend/logs/dev.log

# Error Example
❌ Frontend dependencies not installed
   Run: make install-frontend
   Or: cd frontend && npm install
```

## Integration Points

### Existing Project Structure
- **Backend Directory:** `/backend/` with Poetry configuration
- **Frontend Directory:** `/frontend/` with package.json
- **Root Level:** Makefile placement for global access
- **Documentation:** Integration with existing README.md

### CI/CD Pipeline Alignment
- Makefile targets should mirror GitHub Actions workflow commands
- Test commands must produce compatible output formats
- Coverage reporting should integrate with existing tools

### IDE Integration
- VS Code tasks.json compatibility for IDE task runner
- IntelliJ/PyCharm external tools configuration
- Terminal integration for various development environments

## Acceptance Criteria

### Functional Requirements
- [ ] `make start-backend` successfully starts FastAPI server on port 8000
- [ ] `make start-frontend` successfully starts React server on port 3000
- [ ] `make start-all` starts both servers in background with reliable PID tracking
- [ ] `make stop-all` gracefully terminates all tracked development processes
- [ ] `make test-backend` executes pytest with coverage reporting (>80% threshold)
- [ ] `make test-frontend` executes Jest/RTL tests with proper exit codes
- [ ] `make test-all` runs complete test suite with consolidated reporting
- [ ] `make install` successfully installs all project dependencies
- [ ] `make lint` runs all code quality tools with actionable output
- [ ] `make format` auto-formats all code according to project standards
- [ ] `make clean` removes all build artifacts and cache files
- [ ] `make help` displays comprehensive command documentation

### Technical Requirements
- [ ] Cross-platform compatibility (Linux, macOS, Windows WSL)
- [ ] Proper error handling with informative messages
- [ ] Background process management with reliable cleanup
- [ ] Integration with existing toolchain (Poetry, npm, pytest, Jest)
- [ ] Performance optimization for common development workflows

### Documentation Requirements
- [ ] README.md updated with Makefile usage section
- [ ] Inline Makefile documentation with target descriptions
- [ ] Common workflow examples and troubleshooting guide
- [ ] Integration instructions for various development environments

## Assumptions & Constraints

### Technical Assumptions
- Poetry is configured and available for Python dependency management
- Node.js and npm/yarn are installed for frontend development
- Project structure follows established backend/ and frontend/ directories
- Developers have appropriate permissions for port binding (8000, 3000)

### Performance Constraints
- Server startup should complete within 30 seconds under normal conditions
- Test execution should provide feedback within first 10 seconds
- Background processes must not consume excessive system resources

### Compatibility Constraints
- Must work with GNU Make 3.8+ (standard on most systems)
- Shell commands must be POSIX-compliant for cross-platform support
- No external dependencies beyond standard development tools
- Graceful degradation when optional tools are unavailable
