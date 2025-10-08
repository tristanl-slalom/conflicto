"""
Health check API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.settings import settings
from app.db.database import get_db
from app.models.schemas import ErrorResponse, HealthResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/", response_model=HealthResponse, responses={503: {"model": ErrorResponse}}
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Health check endpoint.

    Returns service health status and checks database connectivity.
    """
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))

        return HealthResponse(
            status="healthy",
            version=settings.version,
            environment=settings.environment,
            app_version=settings.app_version,
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return HealthResponse(
            status="unhealthy",
            version=settings.version,
            environment=settings.environment,
            app_version=settings.app_version,
        )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """
    Readiness check endpoint.

    Returns whether the service is ready to accept requests.
    """
    return HealthResponse(status="ready", version=settings.version)


@router.get("/live", response_model=HealthResponse)
async def liveness_check() -> HealthResponse:
    """
    Liveness check endpoint.

    Returns whether the service is alive and running.
    """
    return HealthResponse(status="alive", version=settings.version)
