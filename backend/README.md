# Caja Backend

FastAPI backend for the Caja live event engagement platform.

## Setup

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
cd backend
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Set up the database:
```bash
poetry run alembic upgrade head
```

5. Run the development server:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with:
```bash
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=app --cov-report=html
```

## Development

Format code:
```bash
poetry run black .
```

Lint code:
```bash
poetry run flake8
poetry run mypy .
```

## Docker

Build and run with Docker:
```bash
docker build -t caja-backend .
docker run -p 8000:8000 caja-backend
```

## Database Migrations

Create a new migration:
```bash
poetry run alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
poetry run alembic upgrade head
```
