#!/bin/bash
# Run tests

set -e

cd backend

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_info "Running tests..."
poetry run pytest

log_info "Running code quality checks..."
poetry run black --check app tests
poetry run isort --check-only app tests
poetry run flake8 app tests
poetry run mypy app
