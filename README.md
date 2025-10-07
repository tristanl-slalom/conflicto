# 🎯 Conflicto - Caja Live Event Engagement Platform

A powerful real-time event engagement platform for interactive presentations, Q&A sessions, and audience participation.

## 🚀 Quick Start

Get up and running in under 5 minutes:

```bash
# Clone the repository
git clone <repository-url>
cd conflicto

# Run the automated setup
make setup

# Start development
make dev
```

That's it! The Makefile handles everything you need and starts the development environment.

### Alternative Setup Methods

**Direct backend scripts (if you prefer):**
```bash
cd backend
./setup.sh    # Setup
./start-dev.sh # Start development
```

**Manual setup:**
```bash
cd backend
poetry install
cp .env.example .env
# Edit .env as needed
```

## 📋 What Gets Installed

The setup script automatically installs and configures:

- ✅ **Homebrew** (macOS package manager)
- ✅ **Python 3.11** (required version)
- ✅ **Poetry** (dependency management)
- ✅ **Docker & Docker Compose** (database services)
- ✅ **PostgreSQL** (main database)
- ✅ **Redis** (caching/sessions)
- ✅ **All Python dependencies**
- ✅ **Pre-commit hooks**
- ✅ **Development utilities**

## 🛠️ Development Commands

Use these Make commands from the project root (recommended):

```bash
make help     # 📋 Show all available commands
make setup    # 🚀 Complete project setup
make dev      # 🟢 Start development environment (alias: make start)
make stop     # 🔴 Stop development environment
make test     # 🧪 Run all tests and quality checks
make reset-db # 💥 Reset database (destructive)
```

**💡 Pro tip:** Run `make help` to see all available commands including database operations, Docker commands, and more!

**Alternative - Backend scripts directly:**
```bash
# From backend/ directory
cd backend && ./start-dev.sh  # Start development
cd backend && ./stop-dev.sh   # Stop development
cd backend && ./run-tests.sh  # Run tests
cd backend && ./reset-db.sh   # Reset database
```

## 🌐 Access Your Application

Once started, you can access:

- **API Documentation**: http://localhost:8000/docs
- **FastAPI Application**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/v1/health/

## 📁 Project Structure

```
conflicto/
├── backend/                # FastAPI backend
│   ├── app/               # Application code
│   ├── tests/             # Test suite
│   ├── migrations/        # Database migrations
│   ├── docker-compose.yml # Local services
│   ├── setup.sh          # Backend setup script
│   ├── start-dev.sh      # Start development
│   ├── stop-dev.sh       # Stop development
│   ├── run-tests.sh      # Run tests
│   └── reset-db.sh       # Reset database
├── docs/                  # Documentation
│   ├── DEVELOPMENT.md     # Development guide
│   └── SETUP_SUMMARY.md   # Setup summary
├── Makefile              # Full-stack Make commands
└── README.md             # This file
```

## 🧪 Testing

Run the complete test suite:

```bash
make test
```

**Alternative - Direct backend script:**
```bash
cd backend && ./run-tests.sh
```

This runs:
- Unit tests
- Code formatting checks (Black)
- Import sorting (isort)
- Linting (flake8)
- Type checking (mypy)

## 🔧 Manual Setup

If you prefer to set up manually or need to troubleshoot, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed instructions.

## 📚 Documentation

- [Development Guide](docs/DEVELOPMENT.md) - Comprehensive setup and development instructions
- [Setup Summary](docs/SETUP_SUMMARY.md) - Complete overview of the setup process
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (after starting)

## 🚨 Troubleshooting

### Common Issues

1. **"command not found: poetry"**
   ```bash
   brew install poetry
   ```

2. **"Docker is not running"**
   - Start Docker Desktop
   - Verify: `docker info`

3. **Port conflicts**
   - Stop services using ports 8000, 5432, 6379
   - Or modify ports in `backend/docker-compose.yml`

4. **Python version issues**
   ```bash
   cd backend
   poetry env use /opt/homebrew/bin/python3.11
   poetry install
   ```

### Get Help

If you encounter issues:

1. Check [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed troubleshooting
2. Run `make env-info` to check your environment
3. Try resetting: `make setup`

## 🤝 Contributing

1. Run tests: `make test`
2. Ensure code quality checks pass
3. Pre-commit hooks will run automatically

## 📄 License

[Your License Here]

---

**Need help?** Check the [Development Guide](docs/DEVELOPMENT.md) or run `make help` for all available commands.
