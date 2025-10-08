"""
Test configuration and fixtures.
"""

import asyncio
import os
from collections.abc import AsyncGenerator
from typing import Generator

import pytest

# TestClient import removed - using only AsyncClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

# Set test environment variables before importing the app
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DEBUG", "true")

from app.db.database import Base, get_db

# Test database URLs - Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
SYNC_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engines
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

sync_test_engine = create_engine(
    SYNC_TEST_DATABASE_URL,
    echo=False,
)

# Create test session factories
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

SyncTestSessionLocal = sessionmaker(
    bind=sync_test_engine,
    class_=Session,
    expire_on_commit=False,
)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Get test database session."""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_test_db() -> Generator[Session, None, None]:
    """Get sync test database session."""
    with SyncTestSessionLocal() as session:
        try:
            yield session
        finally:
            session.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create and cleanup test database for each test."""
    # Create all tables once
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Provide clean session
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

    # Clean up tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Removed sync_db_session - using only async database now


@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client with shared test database session."""
    from app.main import app

    async def get_test_db_override():
        yield db_session

    app.dependency_overrides[get_db] = get_test_db_override

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


# Removed sync client - using only async_client now


@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        "title": "Test Session",
        "description": "A test session for unit tests",
        "max_participants": 50,
    }


@pytest.fixture
def sample_session_create():
    """Sample SessionCreate object for testing."""
    from app.models.schemas import SessionCreate

    return SessionCreate(
        title="Test Session",
        description="A test session for unit tests",
        max_participants=50,
    )
