"""
Logging configuration for the Caja backend application.
"""
import logging
import sys
from typing import Any

import structlog
from structlog.typing import FilteringBoundLogger

from app.core.settings import settings


def configure_logging() -> FilteringBoundLogger:
    """Configure structured logging."""

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
            if settings.debug
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if settings.debug else logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.debug else logging.INFO,
    )

    # Get logger
    logger = structlog.get_logger()

    return logger


def get_logger(name: str | None = None) -> FilteringBoundLogger:
    """Get a logger instance."""
    logger = structlog.get_logger()
    if name:
        logger = logger.bind(logger_name=name)
    return logger


def log_request(request_id: str, method: str, path: str, **kwargs) -> None:
    """Log incoming request."""
    logger = get_logger("request")
    logger.info(
        "Request received", request_id=request_id, method=method, path=path, **kwargs
    )


def log_response(
    request_id: str, status_code: int, duration_ms: float, **kwargs
) -> None:
    """Log outgoing response."""
    logger = get_logger("response")
    logger.info(
        "Response sent",
        request_id=request_id,
        status_code=status_code,
        duration_ms=duration_ms,
        **kwargs,
    )


def log_error(error: Exception, context: dict[str, Any] | None = None) -> None:
    """Log an error with context."""
    logger = get_logger("error")
    logger.error(
        "Error occurred",
        error=str(error),
        error_type=type(error).__name__,
        **(context or {}),
    )
