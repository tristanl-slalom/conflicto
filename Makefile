# =============================================================================
# Conflicto - Full-Stack Development Environment
# =============================================================================
# This Makefile provides development commands for the Conflicto project.
# Currently supports: Backend (FastAPI)
# Future: Frontend (React/Next.js), Docker orchestration, CI/CD
#
# Usage:
#   make help           - Show all available commands
#   make setup          - Initial project setup
#   make dev            - Start development environment
#   make test           - Run all tests
#   make clean          - Clean all build artifacts
#
# Structure:
#   backend/            - FastAPI backend application
#   frontend/           - Frontend application (coming soon)
#   docs/              - Project documentation
# =============================================================================

.PHONY: help setup dev start stop test clean reset-db format lint type-check docker-build docker-push

# Default target - show help
help:
	@echo ""
	@echo "🎯 Conflicto Development Commands"
	@echo "=================================="
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make setup          🚀 Complete project setup (backend + future frontend)"
	@echo "  make install        📋 Install all dependencies"
	@echo ""
	@echo "🔥 Development:"
	@echo "  make dev            🟢 Start full development environment"
	@echo "  make start          🟢 Alias for 'dev'"
	@echo "  make stop           🔴 Stop all development services"
	@echo "  make restart        🔄 Restart development environment"
	@echo "  make logs           📋 Show application logs"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  make migrate        ⬆️  Run database migrations"
	@echo "  make migration      ✨ Create new migration (requires MESSAGE='description')"
	@echo "  make reset-db       💥 Reset database (DESTRUCTIVE)"
	@echo "  make db-shell       🐘 Open PostgreSQL shell"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test           🧪 Run all tests (backend + future frontend)"
	@echo "  make test-cov       📊 Run tests with coverage report"
	@echo "  make format         ✨ Format all code (black, isort, prettier)"
	@echo "  make lint           🔍 Run linting (flake8, eslint)"
	@echo "  make type-check     🔒 Run type checking (mypy, tsc)"
	@echo "  make quality        ⭐ Run all quality checks"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build   🔨 Build Docker images"
	@echo "  make docker-run     🚀 Run with Docker Compose"
	@echo "  make docker-push    📤 Push to registry (requires REGISTRY)"
	@echo ""
	@echo "🧹 Utilities:"
	@echo "  make clean          🧹 Clean cache and temp files"
	@echo "  make env-info       ℹ️  Show environment information"
	@echo ""
	@echo "📚 Components:"
	@echo "  Backend:  FastAPI application in backend/"
	@echo "  Frontend: Coming soon..."
	@echo "  Docs:     Documentation in docs/"
	@echo ""

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================
# Complete project setup - currently backend only, will include frontend
setup:
	@echo "🚀 Setting up Conflicto development environment..."
	@echo "📦 Backend setup..."
	cd backend && chmod +x setup.sh && ./setup.sh
	@echo ""
	@echo "✅ Setup complete!"
	@echo "📝 Next: Run 'make dev' to start development"

# Install dependencies for all components
install:
	@echo "📦 Installing backend dependencies..."
	cd backend && poetry install
	@echo "📦 Frontend dependencies will be added here..."
	# TODO: Add frontend dependency installation
	@echo "✅ All dependencies installed!"

# =============================================================================
# DEVELOPMENT ENVIRONMENT
# =============================================================================

# Start full development environment (alias: start)
dev: start

# Start development environment
start:
	@echo "🟢 Starting Conflicto development environment..."
	@echo "🎯 Backend: Starting FastAPI server..."
	cd backend && ./start-dev.sh

# Stop development environment
stop:
	@echo "🔴 Stopping Conflicto development environment..."
	cd backend && ./stop-dev.sh
	@echo "🛑 Frontend stop commands will be added here..."
	# TODO: Add frontend stop commands

# Restart everything
restart: stop start

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

# Run all tests (backend + future frontend)
test:
	@echo "🧪 Running all tests..."
	@echo "🎯 Backend tests..."
	cd backend && ./run-tests.sh
	@echo "🎯 Frontend tests will be added here..."
	# TODO: Add frontend test commands

# Run tests with coverage
test-cov:
	@echo "📊 Running tests with coverage..."
	cd backend && poetry run pytest --cov=app --cov-report=html --cov-report=term

# Format all code
format:
	@echo "✨ Formatting all code..."
	@echo "🐍 Python (black, isort)..."
	cd backend && poetry run black app tests
	cd backend && poetry run isort app tests
	@echo "🌐 Frontend formatting will be added here..."
	# TODO: Add prettier, etc.

# Run linting
lint:
	@echo "🔍 Running linting..."
	@echo "🐍 Python (flake8)..."
	cd backend && poetry run flake8 app tests
	@echo "🌐 Frontend linting will be added here..."
	# TODO: Add eslint, etc.

# Run type checking
type-check:
	@echo "🔒 Running type checking..."
	@echo "🐍 Python (mypy)..."
	cd backend && poetry run mypy app
	@echo "🌐 TypeScript checking will be added here..."
	# TODO: Add tsc, etc.

# Run all quality checks
quality: format lint type-check test
	@echo "⭐ All quality checks completed!"

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
	@echo "🐍 Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd backend && rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "🌐 Frontend cache will be cleaned here..."
	# TODO: Add node_modules, .next, etc. cleanup
	@echo "✅ Cleanup complete!"

# Show environment information
env-info:
	@echo "ℹ️  Environment Information"
	@echo "=========================="
	@echo "🖥️  System:"
	@uname -a
	@echo ""
	@echo "🐍 Python:"
	@which python3 2>/dev/null || echo "  Not found"
	@python3 --version 2>/dev/null || echo "  Version unavailable"
	@echo ""
	@echo "📦 Poetry:"
	@which poetry 2>/dev/null || echo "  Not found"
	@poetry --version 2>/dev/null || echo "  Version unavailable"
	@echo ""
	@echo "🐳 Docker:"
	@which docker 2>/dev/null || echo "  Not found"
	@docker --version 2>/dev/null || echo "  Version unavailable"
	@echo ""
	@echo "🎯 Backend Environment:"
	@if [ -d "backend" ]; then \
		cd backend && poetry env info 2>/dev/null || echo "  No Poetry environment configured"; \
	else \
		echo "  Backend directory not found"; \
	fi
	@echo ""
	@echo "🌐 Frontend Environment:"
	@echo "  Will be added when frontend is implemented"

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
