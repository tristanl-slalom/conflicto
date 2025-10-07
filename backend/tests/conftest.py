"""
Test configuration and fixtures.
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import settings
from app.db.database import Base, get_db
from app.main import app

# Test database URLs
TEST_DATABASE_URL = (
    "postgresql+asyncpg://caja_user:caja_password@localhost:5432/caja_test_db"
)
SYNC_TEST_DATABASE_URL = (
    "postgresql://caja_user:caja_password@localhost:5432/caja_test_db"
)

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


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create and cleanup test database."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Provide session
    async with TestSessionLocal() as session:
        yield session

    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def sync_db_session() -> Generator[Session, None, None]:
    """Create and cleanup sync test database."""
    # Create all tables
    Base.metadata.create_all(bind=sync_test_engine)

    # Provide session
    with SyncTestSessionLocal() as session:
        yield session

    # Drop all tables
    Base.metadata.drop_all(bind=sync_test_engine)


@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client with test database."""
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def client(sync_db_session: Session) -> TestClient:
    """Create test client with sync test database."""
    app.dependency_overrides[get_db] = lambda: sync_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


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
