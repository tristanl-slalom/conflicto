#!/bin/bash
# Start development environment

set -e

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

cd backend

# Start Docker services
log_info "Starting Docker services..."
docker-compose up -d postgres redis

# Wait for PostgreSQL
log_info "Waiting for PostgreSQL..."
while ! docker-compose exec -T postgres pg_isready -U caja_user -d caja_db &> /dev/null; do
    sleep 1
done

# Run migrations
log_info "Running database migrations..."
poetry run alembic upgrade head

# Start the application
log_success "Starting FastAPI application..."
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
