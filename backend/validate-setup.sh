#!/bin/bash

# Validation script to check if setup was successful

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "🔍 Validating Caja Backend Setup"
echo "================================"

# Check if we're in the right directory
if [ ! -f "backend/pyproject.toml" ]; then
    log_error "Not in project root directory. Please run from conflicto/ directory."
    exit 1
fi

# Check Poetry
if command -v poetry &> /dev/null; then
    log_success "Poetry is installed"
    cd backend
    
    # Check virtual environment
    if poetry env info &> /dev/null; then
        log_success "Poetry virtual environment exists"
        
        # Check Python version
        python_version=$(poetry run python --version 2>&1 | grep -o "3\.11\.[0-9]*" || echo "")
        if [ -n "$python_version" ]; then
            log_success "Python 3.11 ($python_version) is configured"
        else
            log_error "Python 3.11 not found in virtual environment"
            exit 1
        fi
        
        # Check if dependencies are installed
        if poetry run python -c "import fastapi, sqlalchemy, alembic" &> /dev/null; then
            log_success "Key dependencies are installed"
        else
            log_error "Dependencies not properly installed"
            exit 1
        fi
    else
        log_error "Poetry virtual environment not found"
        exit 1
    fi
    cd ..
else
    log_error "Poetry not found"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    log_success "Docker is installed"
    
    if docker info &> /dev/null; then
        log_success "Docker is running"
    else
        log_warning "Docker is installed but not running (start Docker Desktop)"
    fi
else
    log_warning "Docker not found (install Docker Desktop for full functionality)"
fi

# Check if utility scripts exist and are executable
scripts=("start-dev.sh" "stop-dev.sh" "run-tests.sh" "reset-db.sh")
for script in "${scripts[@]}"; do
    if [ -x "$script" ]; then
        log_success "Script $script is ready"
    else
        log_warning "Script $script missing or not executable"
    fi
done

# Check environment file
if [ -f "backend/.env" ]; then
    log_success "Environment file (.env) exists"
else
    log_warning "Environment file (.env) not found - will use defaults"
fi

# Test basic import
echo ""
echo "🧪 Testing basic application import..."
cd backend
if poetry run python -c "from app.main import app; print('FastAPI app imported successfully')" 2>/dev/null; then
    log_success "Application imports successfully"
    import_success=true
else
    log_warning "Application import test failed (may need environment setup)"
    import_success=false
fi
cd ..

echo ""
if [ "$import_success" = true ]; then
    echo "🎉 Setup validation complete!"
else
    echo "⚠️  Setup validation completed with warnings"
fi
echo ""
echo "Next steps:"
echo "1. Run: ./start-dev.sh (or ./setup.sh if scripts missing)"
echo "2. Visit: http://localhost:8000/docs"
echo "3. Run tests: ./run-tests.sh"