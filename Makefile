# =============================================================================
# Conflicto - Full-Stack Development Environment
# =============================================================================
# This Makefile provides development commands for the Conflicto project.
# Supports: Backend (FastAPI), Frontend (React+Vite), Process Management
#
# Usage:
#   make help           - Show all available commands
#   make setup          - Initial project setup
#   make start-all      - Start both backend and frontend servers
#   make test           - Run all tests
#   make clean          - Clean all build artifacts
#
# Structure:
#   backend/            - FastAPI backend application
#   frontend/           - React+TypeScript frontend application
#   docs/              - Project documentation
#   .dev-processes/     - Process tracking directory (auto-created)
# =============================================================================

# Configuration variables
BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 3000
BACKEND_DIR = backend
FRONTEND_DIR = frontend
PYTHON_EXEC ?= python3
NODE_PACKAGE_MANAGER ?= npm
PROCESS_DIR = .dev-processes

# Ensure process directory exists
$(shell mkdir -p $(PROCESS_DIR))

.PHONY: help setup dev start stop test clean reset-db format lint type-check docker-build docker-push
.PHONY: start-backend start-frontend start-all stop-all restart-all status
.PHONY: test-backend test-frontend test-all test-watch test-coverage
.PHONY: install install-backend install-frontend lint-backend lint-frontend
.PHONY: format-backend format-frontend quality
.PHONY: ci ci-backend ci-frontend ci-security ci-build ci-validate ci-full

# Default target - show help
help:
	@echo ""
	@echo "🎯 Conflicto Development Commands"
	@echo "=================================="
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make setup            🚀 Complete project setup (backend + frontend)"
	@echo "  make install          📋 Install all dependencies"
	@echo "  make install-backend  🐍 Install backend dependencies only"
	@echo "  make install-frontend � Install frontend dependencies only"
	@echo ""
	@echo "�🔥 Development Servers:"
	@echo "  make start-backend    🟢 Start FastAPI server (port $(BACKEND_PORT))"
	@echo "  make start-frontend   🟢 Start React server (port $(FRONTEND_PORT))"
	@echo "  make start-all        � Start both servers in background"
	@echo "  make stop-all         🔴 Stop all development servers"
	@echo "  make restart-all      🔄 Restart all servers"
	@echo "  make status           📊 Show server status"
	@echo "  make dev              🟢 Alias for 'start-all'"
	@echo "  make start            🟢 Alias for 'start-all'"
	@echo "  make stop             🔴 Alias for 'stop-all'"
	@echo "  make restart          🔄 Alias for 'restart-all'"
	@echo "  make logs             📋 Show application logs"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  make migrate          ⬆️  Run database migrations"
	@echo "  make migration        ✨ Create new migration (requires MESSAGE='description')"
	@echo "  make reset-db         💥 Reset database (DESTRUCTIVE)"
	@echo "  make db-shell         🐘 Open PostgreSQL shell"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test             🧪 Run all tests (backend + frontend)"
	@echo "  make test-backend     🐍 Run backend tests only"
	@echo "  make test-frontend    ⚛️  Run frontend tests only"
	@echo "  make test-watch       👀 Run tests in watch mode"
	@echo "  make test-coverage    📊 Run tests with coverage report"
	@echo "  make format           ✨ Format all code (black + prettier)"
	@echo "  make format-backend   🐍 Format backend code only"
	@echo "  make format-frontend  ⚛️  Format frontend code only"
	@echo "  make lint             🔍 Run all linting (flake8 + eslint)"
	@echo "  make lint-backend     🐍 Run backend linting only"
	@echo "  make lint-frontend    ⚛️  Run frontend linting only"
	@echo "  make type-check       🔒 Run type checking (mypy + tsc)"
	@echo "  make quality          ⭐ Run all quality checks"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build     🔨 Build Docker images"
	@echo "  make docker-run       🚀 Run with Docker Compose"
	@echo "  make docker-push      📤 Push to registry (requires REGISTRY)"
	@echo ""
	@echo "🧹 Utilities:"
	@echo "  make clean            🧹 Clean cache and temp files"
	@echo "  make env-info         ℹ️  Show environment information"
	@echo ""
	@echo "📚 Components:"
	@echo "  Backend:  FastAPI application in backend/ (Python $(shell python3 --version 2>/dev/null | cut -d' ' -f2 || echo 'N/A'))"
	@echo "  Frontend: React+TypeScript in frontend/ (Node $(shell node --version 2>/dev/null || echo 'N/A'))"
	@echo "  Docs:     Documentation in docs/"
	@echo ""

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================

# Complete project setup - backend and frontend
setup: install
	@echo "🚀 Setting up Conflicto development environment..."
	@if [ -d "$(BACKEND_DIR)" ]; then \
		echo "📦 Backend setup..."; \
		cd $(BACKEND_DIR) && chmod +x setup.sh && ./setup.sh; \
	else \
		echo "⚠️  Backend directory not found, skipping backend setup"; \
	fi
	@echo "✅ Setup complete!"
	@echo "📝 Next: Run 'make start-all' to start development servers"

# Install dependencies for all components
install: install-backend install-frontend

# Install backend dependencies
install-backend:
	@echo "📦 Installing backend dependencies..."
	@if [ ! -d "$(BACKEND_DIR)" ]; then \
		echo "❌ Backend directory '$(BACKEND_DIR)' not found"; \
		exit 1; \
	fi
	@if ! command -v poetry >/dev/null 2>&1; then \
		echo "❌ Poetry not found. Please install Poetry first:"; \
		echo "   curl -sSL https://install.python-poetry.org | python3 -"; \
		exit 1; \
	fi
	cd $(BACKEND_DIR) && poetry install
	@echo "✅ Backend dependencies installed!"

# Install frontend dependencies
install-frontend:
	@echo "📦 Installing frontend dependencies..."
	@if [ ! -d "$(FRONTEND_DIR)" ]; then \
		echo "❌ Frontend directory '$(FRONTEND_DIR)' not found"; \
		exit 1; \
	fi
	@if ! command -v node >/dev/null 2>&1; then \
		echo "❌ Node.js not found. Please install Node.js first"; \
		exit 1; \
	fi
	@if command -v yarn >/dev/null 2>&1; then \
		echo "📦 Using Yarn..."; \
		cd $(FRONTEND_DIR) && yarn install; \
	else \
		echo "📦 Using npm..."; \
		cd $(FRONTEND_DIR) && npm install; \
	fi
	@echo "✅ Frontend dependencies installed!"

# =============================================================================
# DEVELOPMENT ENVIRONMENT - SERVER MANAGEMENT
# =============================================================================

# Helper function to check if port is available
define check_port
	@if lsof -Pi :$(1) -sTCP:LISTEN -t >/dev/null 2>&1; then \
		echo "⚠️  Port $(1) is already in use"; \
		lsof -Pi :$(1) -sTCP:LISTEN; \
		exit 1; \
	fi
endef

# Helper function to stop process by PID file
define stop_process
	@if [ -f "$(PROCESS_DIR)/$(1).pid" ]; then \
		PID=$$(cat $(PROCESS_DIR)/$(1).pid 2>/dev/null); \
		if [ -n "$$PID" ] && kill -0 $$PID 2>/dev/null; then \
			echo "🔴 Stopping $(1) (PID: $$PID)..."; \
			kill $$PID 2>/dev/null || true; \
			sleep 2; \
			if kill -0 $$PID 2>/dev/null; then \
				echo "⚠️  Force killing $(1)..."; \
				kill -9 $$PID 2>/dev/null || true; \
			fi; \
		fi; \
		rm -f $(PROCESS_DIR)/$(1).pid; \
	fi
endef

# Start backend server only
start-backend:
	@echo "🟢 Starting backend server on port $(BACKEND_PORT)..."
	@if [ ! -d "$(BACKEND_DIR)" ]; then \
		echo "❌ Backend directory '$(BACKEND_DIR)' not found"; \
		exit 1; \
	fi
	$(call check_port,$(BACKEND_PORT))
	@cd $(BACKEND_DIR) && \
		poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT) & \
		echo $$! > ../$(PROCESS_DIR)/backend.pid
	@echo "✅ Backend server started"
	@echo "   📍 URL: http://localhost:$(BACKEND_PORT)"
	@echo "   📍 API Docs: http://localhost:$(BACKEND_PORT)/docs"
	@echo "   📄 PID: $$(cat $(PROCESS_DIR)/backend.pid)"

# Start frontend server only
start-frontend:
	@echo "🟢 Starting frontend server on port $(FRONTEND_PORT)..."
	@if [ ! -d "$(FRONTEND_DIR)" ]; then \
		echo "❌ Frontend directory '$(FRONTEND_DIR)' not found"; \
		exit 1; \
	fi
	$(call check_port,$(FRONTEND_PORT))
	@cd $(FRONTEND_DIR) && \
		npm run dev & \
		echo $$! > ../$(PROCESS_DIR)/frontend.pid
	@echo "✅ Frontend server started"
	@echo "   📍 URL: http://localhost:$(FRONTEND_PORT)"
	@echo "   📄 PID: $$(cat $(PROCESS_DIR)/frontend.pid)"

# Start all servers in background
start-all:
	@echo "🚀 Starting all development servers..."
	@$(MAKE) start-backend
	@sleep 2
	@$(MAKE) start-frontend
	@echo ""
	@echo "✅ All servers started successfully!"
	@echo "📊 Run 'make status' to check server status"
	@echo "🔴 Run 'make stop-all' to stop all servers"

# Stop all servers
stop-all:
	@echo "🔴 Stopping all development servers..."
	$(call stop_process,backend)
	$(call stop_process,frontend)
	@echo "✅ All servers stopped"

# Restart all servers
restart-all: stop-all
	@sleep 1
	@$(MAKE) start-all

# Check status of development servers
status:
	@echo "📊 Development Server Status"
	@echo "=========================="
	@if [ -f "$(PROCESS_DIR)/backend.pid" ]; then \
		PID=$$(cat $(PROCESS_DIR)/backend.pid 2>/dev/null); \
		if [ -n "$$PID" ] && kill -0 $$PID 2>/dev/null; then \
			echo "� Backend:  Running (PID: $$PID, Port: $(BACKEND_PORT))"; \
		else \
			echo "🔴 Backend:  Stopped (stale PID file)"; \
			rm -f $(PROCESS_DIR)/backend.pid; \
		fi; \
	else \
		echo "🔴 Backend:  Stopped"; \
	fi
	@if [ -f "$(PROCESS_DIR)/frontend.pid" ]; then \
		PID=$$(cat $(PROCESS_DIR)/frontend.pid 2>/dev/null); \
		if [ -n "$$PID" ] && kill -0 $$PID 2>/dev/null; then \
			echo "🟢 Frontend: Running (PID: $$PID, Port: $(FRONTEND_PORT))"; \
		else \
			echo "🔴 Frontend: Stopped (stale PID file)"; \
			rm -f $(PROCESS_DIR)/frontend.pid; \
		fi; \
	else \
		echo "🔴 Frontend: Stopped"; \
	fi
	@echo ""

# Aliases for backward compatibility
dev: start-all
start: start-all
stop: stop-all
restart: restart-all

# Show application logs
logs:
	@echo "📋 Showing backend logs..."
	cd backend && docker-compose logs -f backend

# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

# Run database migrations
migrate:
	@echo "⬆️ Running database migrations..."
	cd backend && poetry run alembic upgrade head

# Create new migration (requires MESSAGE="description")
migration:
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ Error: MESSAGE is required"; \
		echo "Usage: make migration MESSAGE='Add user table'"; \
		exit 1; \
	fi
	@echo "✨ Creating migration: $(MESSAGE)"
	cd backend && poetry run alembic revision --autogenerate -m "$(MESSAGE)"

# Reset database (DESTRUCTIVE)
reset-db:
	@echo "💥 WARNING: This will reset the database!"
	cd backend && ./reset-db.sh

# Open PostgreSQL shell
db-shell:
	@echo "🐘 Opening PostgreSQL shell..."
	cd backend && docker-compose exec postgres psql -U caja_user -d caja_db

# =============================================================================
# TESTING & QUALITY ASSURANCE
# =============================================================================

# Run all tests (backend + frontend)
test: test-backend test-frontend
	@echo "✅ All tests completed!"

# Run backend tests only
test-backend:
	@echo "🧪 Running backend tests..."
	@if [ ! -d "$(BACKEND_DIR)" ]; then \
		echo "❌ Backend directory '$(BACKEND_DIR)' not found"; \
		exit 1; \
	fi
	@if [ -f "$(BACKEND_DIR)/run-tests.sh" ]; then \
		cd $(BACKEND_DIR) && ./run-tests.sh; \
	else \
		cd $(BACKEND_DIR) && poetry run pytest; \
	fi

# Run frontend tests only
test-frontend:
	@echo "🧪 Running frontend tests..."
	@if [ ! -d "$(FRONTEND_DIR)" ]; then \
		echo "❌ Frontend directory '$(FRONTEND_DIR)' not found"; \
		exit 1; \
	fi
	cd $(FRONTEND_DIR) && npm run test

# Run tests in watch mode
test-watch:
	@echo "👀 Starting test watch mode..."
	@echo "Choose which tests to watch:"
	@echo "  1) Backend only    2) Frontend only    3) Both (parallel)"
	@read -p "Enter choice [1-3]: " choice; \
	case $$choice in \
		1) echo "🐍 Watching backend tests..."; cd $(BACKEND_DIR) && poetry run pytest --watch ;; \
		2) echo "⚛️  Watching frontend tests..."; cd $(FRONTEND_DIR) && npm run test -- --watch ;; \
		3) echo "🔄 Watching both..."; \
		   cd $(BACKEND_DIR) && poetry run pytest --watch & \
		   cd $(FRONTEND_DIR) && npm run test -- --watch & \
		   wait ;; \
		*) echo "❌ Invalid choice" ;; \
	esac

# Run tests with comprehensive coverage
test-coverage:
	@echo "📊 Running tests with coverage reporting..."
	@echo "🐍 Backend coverage..."
	cd $(BACKEND_DIR) && poetry run pytest --cov=app --cov-report=html --cov-report=term-missing
	@echo "⚛️  Frontend coverage..."
	cd $(FRONTEND_DIR) && npm run test -- --coverage
	@echo "📊 Coverage reports generated:"
	@echo "   Backend:  $(BACKEND_DIR)/htmlcov/index.html"
	@echo "   Frontend: $(FRONTEND_DIR)/coverage/lcov-report/index.html"

# Legacy alias
test-cov: test-coverage

# Format all code (backend + frontend)
format: format-backend format-frontend
	@echo "✅ All code formatted!"

# Format backend code only
format-backend:
	@echo "✨ Formatting backend code..."
	@if [ ! -d "$(BACKEND_DIR)" ]; then \
		echo "❌ Backend directory '$(BACKEND_DIR)' not found"; \
		exit 1; \
	fi
	cd $(BACKEND_DIR) && poetry run black app tests
	cd $(BACKEND_DIR) && poetry run isort app tests
	@echo "✅ Backend code formatted!"

# Format frontend code only
format-frontend:
	@echo "✨ Formatting frontend code..."
	@if [ ! -d "$(FRONTEND_DIR)" ]; then \
		echo "❌ Frontend directory '$(FRONTEND_DIR)' not found"; \
		exit 1; \
	fi
	@if command -v prettier >/dev/null 2>&1; then \
		cd $(FRONTEND_DIR) && prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"; \
	else \
		echo "⚠️  Prettier not found globally, trying via npm..."; \
		cd $(FRONTEND_DIR) && npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"; \
	fi
	@echo "✅ Frontend code formatted!"

# Run all linting (backend + frontend)
lint: lint-backend lint-frontend
	@echo "✅ All linting completed!"

# Run backend linting only
lint-backend:
	@echo "� Running backend linting..."
	@if [ ! -d "$(BACKEND_DIR)" ]; then \
		echo "❌ Backend directory '$(BACKEND_DIR)' not found"; \
		exit 1; \
	fi
	cd $(BACKEND_DIR) && poetry run flake8 app tests
	@echo "✅ Backend linting completed!"

# Run frontend linting only
lint-frontend:
	@echo "🔍 Running frontend linting..."
	@if [ ! -d "$(FRONTEND_DIR)" ]; then \
		echo "❌ Frontend directory '$(FRONTEND_DIR)' not found"; \
		exit 1; \
	fi
	@if [ -f "$(FRONTEND_DIR)/package.json" ] && grep -q '"lint"' $(FRONTEND_DIR)/package.json; then \
		cd $(FRONTEND_DIR) && npm run lint; \
	else \
		echo "⚠️  No lint script found, trying ESLint directly..."; \
		cd $(FRONTEND_DIR) && npx eslint "src/**/*.{ts,tsx,js,jsx}" --fix || true; \
	fi
	@echo "✅ Frontend linting completed!"

# Run type checking (backend + frontend)
type-check:
	@echo "🔒 Running type checking..."
	@echo "🐍 Python (mypy)..."
	@if [ -d "$(BACKEND_DIR)" ]; then \
		cd $(BACKEND_DIR) && poetry run mypy app; \
	fi
	@echo "🔷 TypeScript..."
	@if [ -d "$(FRONTEND_DIR)" ]; then \
		cd $(FRONTEND_DIR) && npx tsc --noEmit; \
	fi
	@echo "✅ Type checking completed!"

# Run all quality checks
quality: format lint type-check test
	@echo "⭐ All quality checks completed successfully!"

# =============================================================================
# DOCKER OPERATIONS
# =============================================================================
# Build Docker images
docker-build:
	@echo "🔨 Building Docker images..."
	cd backend && docker build -t conflicto-backend .
	@echo "🌐 Frontend Docker build will be added here..."
	# TODO: Add frontend Docker build

# Run with Docker Compose
docker-run:
	@echo "🚀 Running with Docker Compose..."
	cd backend && docker-compose up --build

# Push to registry (requires REGISTRY environment variable)
docker-push:
	@if [ -z "$(REGISTRY)" ]; then \
		echo "❌ Error: REGISTRY is required"; \
		echo "Usage: make docker-push REGISTRY=your-registry.com"; \
		exit 1; \
	fi
	@echo "📤 Pushing to registry: $(REGISTRY)"
	cd backend && docker tag conflicto-backend $(REGISTRY)/conflicto-backend:latest
	cd backend && docker push $(REGISTRY)/conflicto-backend:latest

# =============================================================================
# UTILITIES
# =============================================================================

# Clean cache and temporary files
clean:
	@echo "🧹 Cleaning cache and temporary files..."

	@echo "🐍 Cleaning Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@if [ -d "$(BACKEND_DIR)" ]; then \
		cd $(BACKEND_DIR) && rm -rf htmlcov/ .coverage dist/ build/ *.egg-info/ 2>/dev/null || true; \
	fi

	@echo "⚛️  Cleaning frontend cache..."
	@if [ -d "$(FRONTEND_DIR)" ]; then \
		cd $(FRONTEND_DIR) && rm -rf dist/ build/ coverage/ .vite/ 2>/dev/null || true; \
		cd $(FRONTEND_DIR) && rm -rf node_modules/.cache/ 2>/dev/null || true; \
	fi

	@echo "🔧 Cleaning development files..."
	@rm -rf $(PROCESS_DIR)/ 2>/dev/null || true
	@rm -rf .DS_Store **/.DS_Store 2>/dev/null || true
	@rm -rf *.log **/*.log 2>/dev/null || true

	@echo "✅ Cleanup complete!"

# Show environment information
env-info:
	@echo "ℹ️  Conflicto Development Environment"
	@echo "===================================="
	@echo ""
	@echo "🖥️  System Information:"
	@uname -a
	@echo ""
	@echo "🐍 Python Environment:"
	@printf "  Python:     "
	@python3 --version 2>/dev/null || echo "Not installed"
	@printf "  Poetry:     "
	@poetry --version 2>/dev/null || echo "Not installed"
	@printf "  Pip:        "
	@pip --version 2>/dev/null | cut -d' ' -f1-2 || echo "Not available"
	@echo ""
	@echo "⚛️  Node.js Environment:"
	@printf "  Node.js:    "
	@node --version 2>/dev/null || echo "Not installed"
	@printf "  npm:        "
	@npm --version 2>/dev/null || echo "Not installed"
	@printf "  Yarn:       "
	@yarn --version 2>/dev/null || echo "Not installed"
	@echo ""
	@echo "🐳 Container Environment:"
	@printf "  Docker:     "
	@docker --version 2>/dev/null | cut -d' ' -f1-3 || echo "Not installed"
	@printf "  Compose:    "
	@docker-compose --version 2>/dev/null | cut -d' ' -f1-3 || echo "Not installed"
	@echo ""
	@echo "🎯 Backend Status ($(BACKEND_DIR)/):"
	@if [ -d "$(BACKEND_DIR)" ]; then \
		cd $(BACKEND_DIR) && poetry env info 2>/dev/null || echo "  No Poetry environment configured"; \
		if [ -f "pyproject.toml" ]; then \
			echo "  Project:    $$(grep '^name' pyproject.toml | cut -d'"' -f2) $$(grep '^version' pyproject.toml | cut -d'"' -f2)"; \
		fi; \
	else \
		echo "  ❌ Backend directory not found"; \
	fi
	@echo ""
	@echo "⚛️  Frontend Status ($(FRONTEND_DIR)/):"
	@if [ -d "$(FRONTEND_DIR)" ]; then \
		if [ -f "$(FRONTEND_DIR)/package.json" ]; then \
			echo "  Project:    $$(cd $(FRONTEND_DIR) && node -p 'JSON.parse(require("fs").readFileSync("package.json")).name || "Unknown"') $$(cd $(FRONTEND_DIR) && node -p 'JSON.parse(require("fs").readFileSync("package.json")).version || "0.0.0"')"; \
			echo "  Framework:  React + TypeScript + Vite"; \
		else \
			echo "  ⚠️  No package.json found"; \
		fi; \
	else \
		echo "  ❌ Frontend directory not found"; \
	fi
	@echo ""
	@echo "🔧 Development Configuration:"
	@echo "  Backend Port:  $(BACKEND_PORT)"
	@echo "  Frontend Port: $(FRONTEND_PORT)"
	@echo "  Process Dir:   $(PROCESS_DIR)"
	@echo "  Package Mgr:   $(NODE_PACKAGE_MANAGER)"

# =============================================================================
# DEVELOPMENT SHORTCUTS
# =============================================================================

# Quick access to backend shell
shell:
	@echo "🐚 Entering backend Poetry shell..."
	cd backend && poetry shell

# Run backend directly (without Docker)
run:
	@echo "🏃 Running backend directly..."
	cd backend && poetry run uvicorn app.main:app --reload

# Install pre-commit hooks
pre-commit-install:
	@echo "🪝 Installing pre-commit hooks..."
	cd backend && poetry run pre-commit install

# Run pre-commit on all files
pre-commit-run:
	@echo "🪝 Running pre-commit on all files..."
	cd backend && poetry run pre-commit run --all-files

# =============================================================================
# CI/CD OPERATIONS
# =============================================================================

# Run full CI pipeline locally
ci: ci-backend ci-frontend ci-security ci-build
	@echo "🎉 Full CI pipeline completed successfully!"

# Backend CI checks
ci-backend:
	@echo "🐍 Running backend CI checks..."
	@if [ ! -d "$(BACKEND_DIR)" ]; then \
		echo "❌ Backend directory '$(BACKEND_DIR)' not found"; \
		exit 1; \
	fi
	@echo "📦 Installing backend dependencies..."
	cd $(BACKEND_DIR) && poetry install --no-interaction
	@echo "🧹 Running backend linting (ruff)..."
	cd $(BACKEND_DIR) && poetry run ruff check .
	@echo "💅 Checking backend formatting (ruff)..."
	cd $(BACKEND_DIR) && poetry run ruff format --check .
	@echo "🔒 Running backend type checking (mypy)..."
	cd $(BACKEND_DIR) && poetry run mypy app/
	@echo "🧪 Running backend tests with coverage..."
	cd $(BACKEND_DIR) && ./../.github/scripts/test-backend.sh
	@echo "✅ Backend CI checks completed!"

# Frontend CI checks
ci-frontend:
	@echo "⚛️ Running frontend CI checks..."
	@if [ ! -d "$(FRONTEND_DIR)" ]; then \
		echo "❌ Frontend directory '$(FRONTEND_DIR)' not found"; \
		exit 1; \
	fi
	@echo "📦 Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm ci --prefer-offline --no-audit
	@echo "🧪 Running frontend tests and checks..."
	cd $(FRONTEND_DIR) && ./../.github/scripts/test-frontend.sh
	@echo "✅ Frontend CI checks completed!"

# Security scanning
ci-security:
	@echo "🔒 Running security scanning..."
	@echo "🔍 Filesystem vulnerability scan..."
	@if command -v trivy >/dev/null 2>&1; then \
		trivy fs --severity HIGH,CRITICAL .; \
	else \
		echo "⚠️ Trivy not found - skipping vulnerability scan"; \
		echo "   Install: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin"; \
	fi
	@echo "✅ Security scanning completed!"

# Build validation
ci-build:
	@echo "🔨 Running build validation..."
	@echo "🐍 Building backend..."
	cd $(BACKEND_DIR) && poetry build
	@echo "⚛️ Building frontend..."
	cd $(FRONTEND_DIR) && npm run build
	@echo "✅ Build validation completed!"

# Docker build validation
ci-docker:
	@echo "🐳 Running Docker build validation..."
	@echo "🐍 Building backend Docker image..."
	cd $(BACKEND_DIR) && docker build -t conflicto-backend:ci-test .
	@echo "⚛️ Building frontend Docker image..."
	@if [ -f "$(FRONTEND_DIR)/Dockerfile" ]; then \
		docker build -f $(FRONTEND_DIR)/Dockerfile -t conflicto-frontend:ci-test .; \
	else \
		echo "⚠️ Frontend Dockerfile not found - skipping frontend Docker build"; \
	fi
	@echo "🧪 Testing container startup..."
	@docker run --rm -d --name ci-backend-test conflicto-backend:ci-test || true
	@sleep 5
	@docker stop ci-backend-test 2>/dev/null || true
	@docker rm ci-backend-test 2>/dev/null || true
	@echo "✅ Docker build validation completed!"

# Full CI validation (everything except Docker)
ci-validate: ci-backend ci-frontend ci-security ci-build
	@echo "🎯 Running final validation..."
	@echo "✅ All CI validations passed!"

# Complete CI pipeline with Docker
ci-full: ci-validate ci-docker
	@echo "🏆 Complete CI pipeline finished successfully!"
