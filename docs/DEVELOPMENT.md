# Caja Backend - Development Environment Setup

This repository contains everything needed to run the Caja Live Event Engagement Platform backend locally.

## 🚀 Quick Setup (Recommended)

For a complete automated setup, run:

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Install Homebrew (if needed)
- Install Python 3.11 and Poetry
- Set up the virtual environment
- Install all dependencies
- Start PostgreSQL and Redis
- Run database migrations
- Create utility scripts

## 📋 Manual Setup

If you prefer to set up manually or the automated script doesn't work:

### Prerequisites

1. **macOS** (for the automated script)
2. **Homebrew** - Install from [brew.sh](https://brew.sh/)
3. **Docker Desktop** - Install from [docker.com](https://www.docker.com/products/docker-desktop/)

### Step-by-step Setup

1. **Install Python 3.11 and Poetry**
   ```bash
   brew install python@3.11 poetry
   ```

2. **Navigate to backend directory**
   ```bash
   cd backend
   ```

3. **Configure Poetry to use Python 3.11**
   ```bash
   poetry env use /opt/homebrew/bin/python3.11
   ```

4. **Install dependencies**
   ```bash
   poetry install
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

6. **Start database services**
   ```bash
   docker-compose up -d postgres redis
   ```

7. **Run database migrations**
   ```bash
   poetry run alembic upgrade head
   ```

8. **Set up pre-commit hooks**
   ```bash
   poetry run pre-commit install
   ```

## 🛠️ Development Commands

After setup, use these utility scripts:

```bash
# Start development environment
./start-dev.sh

# Stop development environment
./stop-dev.sh

# Run tests and code quality checks
./run-tests.sh

# Reset database (DESTRUCTIVE - removes all data)
./reset-db.sh
```

## 📖 Manual Development Commands

If you prefer running commands manually:

```bash
cd backend

# Activate virtual environment
poetry shell

# Start the API server
poetry run uvicorn app.main:app --reload

# Run tests
poetry run pytest

# Run code formatting
poetry run black app tests
poetry run isort app tests

# Run linting
poetry run flake8 app tests
poetry run mypy app

# Database operations
poetry run alembic revision --autogenerate -m "description"
poetry run alembic upgrade head
poetry run alembic downgrade -1
```

## 🌐 Services & URLs

After starting the development environment:

- **FastAPI Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/           # Core configuration
│   ├── db/             # Database setup
│   ├── models/         # Pydantic models
│   ├── routes/         # API endpoints
│   └── services/       # Business logic
├── migrations/         # Alembic migrations
├── tests/              # Test suite
├── docker-compose.yml  # Docker services
├── pyproject.toml     # Dependencies
└── .env.example       # Environment template
```

## 🧪 Testing

Run the full test suite:
```bash
./run-tests.sh
```

Or run specific test commands:
```bash
cd backend
poetry run pytest                          # Run all tests
poetry run pytest tests/test_health.py     # Run specific test file
poetry run pytest -v                       # Verbose output
poetry run pytest --cov=app               # With coverage
```

## 🔧 Configuration

Key environment variables in `.env`:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `DEBUG`: Enable debug mode
- `ALLOWED_ORIGINS`: CORS allowed origins

## 🚨 Troubleshooting

### Common Issues

1. **Poetry not found**
   ```bash
   brew install poetry
   ```

2. **Python version issues**
   ```bash
   poetry env use /opt/homebrew/bin/python3.11
   poetry install
   ```

3. **Docker not running**
   - Start Docker Desktop
   - Verify with: `docker info`

4. **Port conflicts**
   - Check if ports 8000, 5432, 6379 are free
   - Stop conflicting services or change ports in docker-compose.yml

5. **Database connection issues**
   ```bash
   docker-compose restart postgres
   # Wait a moment, then:
   poetry run alembic upgrade head
   ```

### Reset Everything

If you need to start fresh:
```bash
./stop-dev.sh
docker-compose down -v  # Remove volumes
./reset-db.sh
./start-dev.sh
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Poetry Documentation](https://python-poetry.org/docs/)

## 🤝 Contributing

1. Make sure all tests pass: `./run-tests.sh`
2. Code is formatted: `poetry run black app tests`
3. No linting errors: `poetry run flake8 app tests`
4. Type checking passes: `poetry run mypy app`

Pre-commit hooks will run these checks automatically.
