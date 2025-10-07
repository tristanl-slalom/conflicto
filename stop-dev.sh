#!/bin/bash
# Stop development environment

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

cd backend

log_info "Stopping Docker services..."
docker-compose down

log_info "Development environment stopped"
