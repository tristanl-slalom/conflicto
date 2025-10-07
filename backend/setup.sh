#!/bin/bash

# Caja Backend - Local Development Environment Setup
# This script sets up everything needed to run the Caja backend locally

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect the operating system and environment
detect_environment() {
    if [[ -n "$CODESPACES" ]]; then
        ENVIRONMENT="codespaces"
        log_info "Detected GitHub Codespaces environment"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        ENVIRONMENT="macos"
        log_info "Detected macOS environment"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        ENVIRONMENT="linux"
        log_info "Detected Linux environment"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check if Homebrew is installed
check_homebrew() {
    log_info "Checking Homebrew installation..."
    if ! command -v brew &> /dev/null; then
        log_warning "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ $(uname -m) == 'arm64' ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        log_success "Homebrew is already installed"
    fi
}

# Install Python 3.11
install_python() {
    log_info "Checking Python 3.11 installation..."
    if ! brew list python@3.11 &> /dev/null; then
        log_info "Installing Python 3.11..."
        brew install python@3.11
    else
        log_success "Python 3.11 is already installed"
    fi
}

# Install Poetry
install_poetry() {
    log_info "Checking Poetry installation..."
    if ! command -v poetry &> /dev/null; then
        log_info "Installing Poetry..."
        brew install poetry
    else
        log_success "Poetry is already installed"
    fi
}

# Install Docker and Docker Compose
install_docker() {
    log_info "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        log_warning "Docker not found. Please install Docker Desktop manually from:"
        log_warning "https://www.docker.com/products/docker-desktop/"
        log_warning "After installation, please restart this script."
        exit 1
    else
        log_success "Docker is already installed"
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is installed but not running. Please start Docker Desktop and try again."
        exit 1
    fi
}

# Setup backend environment
setup_backend() {
    log_info "Setting up backend environment..."
    
    cd backend
    
    # Configure Poetry to use Python 3.11
    log_info "Configuring Poetry to use Python 3.11..."
    poetry env use /opt/homebrew/bin/python3.11 || poetry env use /usr/local/bin/python3.11 || poetry env use python3.11
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    poetry install
    
    # Copy environment file
    if [ ! -f .env ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_warning "Please review and update the .env file with your specific configuration"
    else
        log_success ".env file already exists"
    fi
    
    # Setup pre-commit hooks
    log_info "Setting up pre-commit hooks..."
    poetry run pre-commit install
    
    cd ..
}

# Start services
start_services() {
    log_info "Starting Docker services..."
    cd backend
    
    # Start PostgreSQL and Redis
    docker-compose up -d postgres redis
    
    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    timeout=30
    while ! docker-compose exec -T postgres pg_isready -U caja_user -d caja_db &> /dev/null; do
        sleep 1
        timeout=$((timeout - 1))
        if [ $timeout -eq 0 ]; then
            log_error "PostgreSQL failed to start within 30 seconds"
            exit 1
        fi
    done
    
    log_success "PostgreSQL is ready"
    
    # Run database migrations
    log_info "Running database migrations..."
    poetry run alembic upgrade head
    
    cd ..
}

# Create useful scripts
create_scripts() {
    log_info "Creating utility scripts..."
    
    # Create start script
    cat > start-dev.sh << 'EOF'
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

EOF

    # Create stop script
    cat > stop-dev.sh << 'EOF'
#!/bin/bash
# Stop development environment

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

cd backend

log_info "Stopping Docker services..."
docker-compose down

log_info "Development environment stopped"
EOF

    # Create test script
    cat > run-tests.sh << 'EOF'
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
EOF

    # Create reset database script
    cat > reset-db.sh << 'EOF'
#!/bin/bash
# Reset database

set -e

cd backend

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

log_warning "This will completely reset the database. All data will be lost!"
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Stopping backend service..."
    docker-compose stop backend
    
    log_info "Dropping and recreating database..."
    docker-compose exec postgres psql -U caja_user -d postgres -c "DROP DATABASE IF EXISTS caja_db;"
    docker-compose exec postgres psql -U caja_user -d postgres -c "CREATE DATABASE caja_db;"
    
    log_info "Running migrations..."
    poetry run alembic upgrade head
    
    log_info "Database reset complete"
else
    log_info "Database reset cancelled"
fi
EOF

    # Make scripts executable
    chmod +x start-dev.sh stop-dev.sh run-tests.sh reset-db.sh
    
    log_success "Utility scripts created: start-dev.sh, stop-dev.sh, run-tests.sh, reset-db.sh"
}

# Display usage information
show_usage() {
    echo ""
    log_success "🎉 Setup complete! Here's how to use your development environment:"
    echo ""
    echo "📁 Project structure:"
    echo "   ./start-dev.sh    - Start the development environment"
    echo "   ./stop-dev.sh     - Stop the development environment"
    echo "   ./run-tests.sh    - Run tests and code quality checks"
    echo "   ./reset-db.sh     - Reset the database (DESTRUCTIVE)"
    echo ""
    echo "🚀 Quick start:"
    echo "   1. Run: ./start-dev.sh"
    echo "   2. Open: http://localhost:8000/docs (API documentation)"
    echo "   3. API base URL: http://localhost:8000/api/v1"
    echo ""
    echo "🔧 Manual commands:"
    echo "   cd backend"
    echo "   poetry shell                    # Activate virtual environment"
    echo "   poetry run uvicorn app.main:app --reload  # Start API server"
    echo "   poetry run pytest              # Run tests"
    echo "   poetry run alembic revision --autogenerate -m \"description\"  # Create migration"
    echo "   poetry run alembic upgrade head  # Run migrations"
    echo ""
    echo "📊 Services:"
    echo "   - FastAPI: http://localhost:8000"
    echo "   - PostgreSQL: localhost:5432"
    echo "   - Redis: localhost:6379"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Review and update backend/.env file"
    echo "   2. Check the API documentation at http://localhost:8000/docs"
    echo "   3. Run tests: ./run-tests.sh"
    echo ""
}

# Main setup function
main() {
    echo ""
    log_info "🚀 Caja Backend - Development Environment Setup"
    echo ""
    
    check_os
    check_homebrew
    install_python
    install_poetry
    install_docker
    setup_backend
    start_services
    create_scripts
    show_usage
    
    echo ""
    log_success "✨ Setup completed successfully!"
    echo ""
}

# Run main function
main "$@"