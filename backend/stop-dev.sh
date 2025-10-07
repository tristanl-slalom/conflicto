#!/bin/bash
# Stop development environment
# Run this from the backend/ directory

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

# Ensure we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: This script must be run from the backend/ directory"
    exit 1
fi

if command -v docker &> /dev/null && docker info &> /dev/null; then
    log_info "Stopping Docker services..."
    docker-compose down
else
    log_info "Docker not available. No services to stop."
fi

log_info "Development environment stopped"