#!/bin/bash
set -e

echo "🧪 Running backend tests..."

# Check if we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Must be run from backend directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run database migrations
echo "📊 Running database migrations..."
poetry run alembic upgrade head

# Run tests with coverage
echo "🔍 Running tests with coverage..."
poetry run pytest \
    --cov=app \
    --cov-report=xml \
    --cov-report=html \
    --cov-report=term-missing \
    --junit-xml=test-results.xml \
    -v \
    "$@"

# Check coverage threshold
echo "📈 Checking coverage threshold..."
poetry run coverage report --fail-under=70

echo "✅ Backend tests completed successfully!"
