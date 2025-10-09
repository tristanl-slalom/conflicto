#!/bin/bash

# Caja Backend - Local Development Environment Setup
# This script sets up everything needed to run the Caja backend locally

set -e  # Exit on any error

# Environment variable
ENVIRONMENT=""

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

# Install package manager (Homebrew for macOS, apt for Linux/Codespaces)
setup_package_manager() {
    if [[ "$ENVIRONMENT" == "macos" ]]; then
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
    elif [[ "$ENVIRONMENT" == "linux" || "$ENVIRONMENT" == "codespaces" ]]; then
        log_info "Updating package manager..."
        sudo apt-get update
        log_success "Package manager updated"
    fi
}

# Install Python 3.11
install_python() {
    log_info "Checking Python installation..."

    if [[ "$ENVIRONMENT" == "macos" ]]; then
        if ! brew list python@3.11 &> /dev/null; then
            log_info "Installing Python 3.11..."
            brew install python@3.11
        else
            log_success "Python 3.11 is already installed"
        fi
    elif [[ "$ENVIRONMENT" == "linux" || "$ENVIRONMENT" == "codespaces" ]]; then
        # Check if Python 3.11+ is available
        if command -v python3.11 &> /dev/null; then
            log_success "Python 3.11 is already installed"
        elif command -v python3.12 &> /dev/null; then
            log_success "Python 3.12 is available (compatible)"
        elif command -v python3 &> /dev/null; then
            PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
            log_info "Found Python $PYTHON_VERSION"
            # Simple version comparison without bc
            MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
            MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
            if [[ $MAJOR -gt 3 ]] || [[ $MAJOR -eq 3 && $MINOR -ge 11 ]]; then
                log_success "Python $PYTHON_VERSION is compatible"
            else
                log_warning "Python $PYTHON_VERSION may not be optimal. Recommend 3.11+"
            fi
        else
            log_error "Python 3 not found. Installing..."
            sudo apt-get install -y python3 python3-pip python3-venv
        fi
    fi
}

# Install Poetry
install_poetry() {
    log_info "Checking Poetry installation..."
    if ! command -v poetry &> /dev/null; then
        log_info "Installing Poetry..."
        if [[ "$ENVIRONMENT" == "macos" ]]; then
            brew install poetry
        elif [[ "$ENVIRONMENT" == "linux" || "$ENVIRONMENT" == "codespaces" ]]; then
            # Install Poetry using the official installer
            curl -sSL https://install.python-poetry.org | python3 -

            # Add Poetry to PATH
            export PATH="$HOME/.local/bin:$PATH"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

            # For Codespaces, also add to .profile
            if [[ "$ENVIRONMENT" == "codespaces" ]]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
            fi
        fi
    else
        log_success "Poetry is already installed"
    fi
}

# Install Docker and Docker Compose
install_docker() {
    log_info "Checking Docker installation..."

    if [[ "$ENVIRONMENT" == "codespaces" ]]; then
        log_success "Docker is pre-installed in Codespaces"
        return 0
    fi

    if ! command -v docker &> /dev/null; then
        if [[ "$ENVIRONMENT" == "macos" ]]; then
            log_warning "Docker not found. Please install Docker Desktop manually from:"
            log_warning "https://www.docker.com/products/docker-desktop/"
            log_warning "After installation, please restart this script."
            exit 1
        elif [[ "$ENVIRONMENT" == "linux" ]]; then
            log_info "Installing Docker..."
            # Install Docker using official script
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            rm get-docker.sh

            # Add user to docker group
            sudo usermod -aG docker $USER
            log_warning "Please log out and back in for Docker group membership to take effect"

            # Install Docker Compose
            sudo apt-get install -y docker-compose-plugin
        fi
    else
        log_success "Docker is already installed"
    fi

    # Check if Docker is running (skip for Codespaces as it may not be started yet)
    if [[ "$ENVIRONMENT" != "codespaces" ]]; then
        if ! docker info &> /dev/null; then
            if [[ "$ENVIRONMENT" == "macos" ]]; then
                log_error "Docker is installed but not running. Please start Docker Desktop and try again."
                exit 1
            elif [[ "$ENVIRONMENT" == "linux" ]]; then
                log_info "Starting Docker service..."
                sudo systemctl start docker
                sudo systemctl enable docker
            fi
        fi
    fi
}

# Setup backend environment
setup_backend() {
    log_info "Setting up backend environment..."

    # Navigate to backend directory (handle both cases where script is run from root or backend dir)
    if [[ -d "backend" ]]; then
        cd backend
    elif [[ -f "setup.sh" && -f "pyproject.toml" ]]; then
        # Already in backend directory
        log_info "Already in backend directory"
    else
        log_error "Cannot find backend directory or pyproject.toml. Please run from project root or backend directory."
        exit 1
    fi

    # Configure Poetry to use the best available Python version
    log_info "Configuring Poetry to use the best available Python version..."
    if [[ "$ENVIRONMENT" == "macos" ]]; then
        poetry env use /opt/homebrew/bin/python3.11 || poetry env use /usr/local/bin/python3.11 || poetry env use python3.11
    elif [[ "$ENVIRONMENT" == "linux" || "$ENVIRONMENT" == "codespaces" ]]; then
        # Try to use the best available Python version
        poetry env use python3.12 || poetry env use python3.11 || poetry env use python3
    fi

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

    # Return to parent directory if we changed into backend
    if [[ -d "../.git" ]]; then
        cd ..
    fi
}

# Start services
start_services() {
    log_info "Starting Docker services..."

    # Navigate to backend directory
    if [[ -d "backend" ]]; then
        cd backend
    elif [[ -f "docker-compose.yml" ]]; then
        # Already in backend directory
        log_info "Already in backend directory"
    else
        log_error "Cannot find backend directory or docker-compose.yml"
        exit 1
    fi

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

    # Return to parent directory if we changed into backend
    if [[ -d "../.git" ]]; then
        cd ..
    fi
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
poetry run flake8 app tests
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
    docker-compose exec -T postgres psql -U caja_user -d postgres -c "DROP DATABASE IF EXISTS caja_db;"
    docker-compose exec -T postgres psql -U caja_user -d postgres -c "CREATE DATABASE caja_db;"

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

# Codespaces-specific setup
setup_codespaces_extras() {
    log_info "Setting up Codespaces-specific configuration..."

    # Set up port forwarding configuration
    if [[ -d ".devcontainer" ]]; then
        log_info "Codespaces devcontainer detected"
    fi

    # Add helpful aliases for Codespaces
    cat >> ~/.bashrc << 'EOF'

# Caja project aliases
alias caja-start='cd /workspaces/conflicto && ./start-dev.sh'
alias caja-stop='cd /workspaces/conflicto && ./stop-dev.sh'
alias caja-test='cd /workspaces/conflicto && ./run-tests.sh'
alias caja-backend='cd /workspaces/conflicto/backend'
alias caja-logs='cd /workspaces/conflicto/backend && docker-compose logs -f'
EOF

    log_success "Codespaces aliases added to ~/.bashrc"
    log_info "Available aliases: caja-start, caja-stop, caja-test, caja-backend, caja-logs"
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

    if [[ "$ENVIRONMENT" == "codespaces" ]]; then
        echo ""
        echo "🚀 Codespaces shortcuts (available after reloading shell):"
        echo "   caja-start        - Start the development environment"
        echo "   caja-stop         - Stop the development environment"
        echo "   caja-test         - Run tests"
        echo "   caja-backend      - Navigate to backend directory"
        echo "   caja-logs         - View application logs"
    fi
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

    detect_environment
    setup_package_manager
    install_python
    install_poetry
    install_docker
    setup_backend
    start_services
    create_scripts
    show_usage

    # Codespaces-specific setup
    if [[ "$ENVIRONMENT" == "codespaces" ]]; then
        setup_codespaces_extras
    fi

    echo ""
    log_success "✨ Setup completed successfully!"
    echo ""
}

# Run main function
main "$@"
