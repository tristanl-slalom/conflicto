#!/bin/bash
set -e

echo "🧪 Running frontend tests..."

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "Error: Must be run from frontend directory"
    exit 1
fi

# Run TypeScript type checking
echo "🔍 Running TypeScript type checking..."
npm run type-check

# Run linting
echo "🧹 Running ESLint..."
npm run lint

# Run format checking
echo "💅 Checking code formatting..."
npm run format:check

# Run tests with coverage
echo "🔍 Running tests with coverage..."
npm run test:coverage

# Check coverage threshold
echo "📈 Checking coverage threshold..."
npm run test:coverage:check

# Build for production to validate
echo "🏗️ Building for production..."
npm run build

echo "✅ Frontend tests completed successfully!"
