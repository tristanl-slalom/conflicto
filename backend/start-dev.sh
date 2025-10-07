#!/bin/bash
# Start development environment
# Run this from the backend/ directory

set -e

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

log_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

# Ensure we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: This script must be run from the backend/ directory"
    exit 1
fi

# Check if Docker is available
if command -v docker &> /dev/null && docker info &> /dev/null; then
    # Start Docker services
    log_info "Starting Docker services..."
    docker-compose up -d postgres redis

    # Wait for PostgreSQL
    log_info "Waiting for PostgreSQL..."
    timeout=30
    while ! docker-compose exec -T postgres pg_isready -U caja_user -d caja_db &> /dev/null; do
        sleep 1
        timeout=$((timeout - 1))
        if [ $timeout -eq 0 ]; then
            log_warning "PostgreSQL failed to start within 30 seconds"
            break
        fi
    done

    if [ $timeout -gt 0 ]; then
        # Run migrations
        log_info "Running database migrations..."
        poetry run alembic upgrade head
    fi
else
    log_warning "Docker not available. Running without database services."
    log_warning "Install Docker Desktop for full functionality."
fi

# Start the application
log_success "Starting FastAPI application..."
log_info "API will be available at: http://localhost:8000"
log_info "API Documentation: http://localhost:8000/docs"
log_info "Press Ctrl+C to stop"

poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
