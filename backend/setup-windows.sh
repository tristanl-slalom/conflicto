#!/bin/bash

# Windows Setup Script for Caja Backend
# Run this in Git Bash or WSL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

check_windows() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        log_info "Running on Windows (Git Bash/MSYS)"
    elif grep -qi microsoft /proc/version 2>/dev/null; then
        log_info "Running on Windows (WSL)"
    else
        log_error "This script is for Windows. Please use setup.sh for macOS/Linux."
        exit 1
    fi
}

install_chocolatey() {
    log_info "Checking Chocolatey installation..."
    if ! command -v choco &> /dev/null; then
        log_warning "Chocolatey not found. Please install manually:"
        log_warning "1. Open PowerShell as Administrator"
        log_warning "2. Run: Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
        log_warning "3. Restart this script after installation"
        exit 1
    else
        log_success "Chocolatey is installed"
    fi
}

install_python() {
    log_info "Checking Python 3.11 installation..."
    if ! python3.11 --version &> /dev/null && ! python --version 2>&1 | grep -q "3.11"; then
        log_info "Installing Python 3.11..."
        choco install python311 -y
    else
        log_success "Python 3.11 is available"
    fi
}

install_poetry() {
    log_info "Checking Poetry installation..."
    if ! command -v poetry &> /dev/null; then
        log_info "Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
    else
        log_success "Poetry is already installed"
    fi
}

install_docker() {
    log_info "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        log_warning "Docker not found. Please install Docker Desktop manually:"
        log_warning "https://www.docker.com/products/docker-desktop/"
        log_warning "After installation, restart this script"
        exit 1
    else
        log_success "Docker is installed"
    fi
}

main() {
    log_info "🚀 Caja Backend - Windows Development Setup"
    check_windows
    install_chocolatey
    install_python
    install_poetry
    install_docker
    
    log_info "Running common setup..."
    # The rest follows the same pattern as the main setup script
    # but with Windows-specific paths and commands
    
    log_success "Windows setup complete! Please run the main setup script now."
}

main "$@"