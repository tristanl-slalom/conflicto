#!/bin/bash
# Reset database
# Run this from the backend/ directory

set -e

# Ensure we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: This script must be run from the backend/ directory"
    exit 1
fi

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

if ! command -v docker &> /dev/null || ! docker info &> /dev/null; then
    log_warning "Docker not available. Cannot reset database."
    log_warning "Install Docker Desktop for database functionality."
    exit 1
fi

log_warning "This will completely reset the database. All data will be lost!"
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Stopping backend service..."
    docker-compose stop backend

    log_info "Dropping and recreating database..."
    docker-compose exec -T postgres psql -U caja_user -d postgres -c "DROP DATABASE IF EXISTS caja_db;"
    docker-compose exec -T postgres psql -U caja_user -d postgres -c "CREATE DATABASE caja_db;"

    log_info "Running migrations..."
    poetry run alembic upgrade head

    log_info "Database reset complete"
else
    log_info "Database reset cancelled"
fi
