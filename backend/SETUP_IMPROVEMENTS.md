# Setup Script Improvements

The setup.sh script has been enhanced to work seamlessly across different environments:

## Supported Environments

- **macOS** - Uses Homebrew for package management
- **Linux** - Uses apt package manager
- **GitHub Codespaces** - Optimized for the Codespaces environment

## Key Features

### Environment Detection
- Automatically detects the current environment (macOS, Linux, or Codespaces)
- Uses appropriate package managers and installation methods for each platform

### Package Management
- **macOS**: Uses Homebrew for Python, Poetry, and other tools
- **Linux/Codespaces**: Uses apt for system packages and official installers for Python tools

### Python Version Handling
- **macOS**: Installs Python 3.11 via Homebrew
- **Linux/Codespaces**: Uses the best available Python version (3.11+ preferred, falls back gracefully)

### Docker Support
- **macOS**: Requires Docker Desktop (provides installation guidance)
- **Linux**: Automatically installs Docker CE via official script
- **Codespaces**: Recognizes pre-installed Docker

### Directory Flexibility
- Can be run from either the project root or the backend directory
- Automatically handles path navigation and cleanup

### Codespaces Enhancements
- Adds helpful bash aliases for common tasks:
  - `caja-start` - Start development environment
  - `caja-stop` - Stop development environment
  - `caja-test` - Run tests
  - `caja-backend` - Navigate to backend directory
  - `caja-logs` - View application logs

## Usage

```bash
# From project root
./backend/setup.sh

# From backend directory
./setup.sh
```

## Generated Utility Scripts

The setup creates convenient scripts for development:

- `start-dev.sh` - Start all services and the FastAPI application
- `stop-dev.sh` - Stop all Docker services
- `run-tests.sh` - Run tests and code quality checks
- `reset-db.sh` - Reset database (destructive operation)

These scripts are created in both the backend directory and project root for convenience.

## What's New

1. **Cross-platform compatibility** - Works on macOS, Linux, and Codespaces
2. **Intelligent environment detection** - Adapts behavior based on the detected environment
3. **Improved error handling** - Better error messages and graceful fallbacks
4. **Codespaces optimization** - Special handling and aliases for GitHub Codespaces
5. **Flexible directory handling** - Works from multiple starting directories
6. **Enhanced user experience** - Environment-specific usage instructions and shortcuts
