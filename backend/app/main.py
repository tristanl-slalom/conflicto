"""
FastAPI main application module.

This is the entry point for the Caja backend application.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import configure_logging, get_logger
from app.core.settings import settings
from app.routes import health, sessions, user_responses, activities, participants
from app.services.activity_framework.registration import register_activity_types

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Caja Live Event Engagement Platform Backend API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(sessions.router, prefix=settings.api_v1_prefix)
app.include_router(participants.router, prefix=settings.api_v1_prefix)
app.include_router(user_responses.router)
app.include_router(activities.router)


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info("Starting Caja backend application", version=settings.version)

    # Register activity types with the framework
    try:
        register_activity_types()
        logger.info("Activity framework initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize activity framework: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info("Shutting down Caja backend application")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.project_name,
        "version": settings.version,
        "status": "running",
        "docs_url": "/docs",
        "api_prefix": settings.api_v1_prefix,
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
