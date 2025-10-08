#!/bin/bash
# Run tests
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

log_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

log_info "Running tests..."
poetry run pytest

log_info "Running code quality checks..."
poetry run black --check app tests

log_success "All tests and quality checks passed!"
