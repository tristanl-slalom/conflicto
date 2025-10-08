#!/usr/bin/env python3
"""
Database migration runner for CI/CD deployment pipeline.

Executes Alembic database migrations safely during deployment.
"""

import logging
import sys
from pathlib import Path

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.settings import settings  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """Execute database migrations using Alembic."""
    try:
        logger.info(
            f"Starting database migrations for environment: {settings.environment}"
        )

        # Configure Alembic
        alembic_cfg = Config(str(backend_dir / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

        # Check database connectivity
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connectivity verified")

        # Show current migration status
        logger.info("Current migration status:")
        command.current(alembic_cfg)

        # Run migrations
        logger.info("Executing migrations...")
        command.upgrade(alembic_cfg, "head")

        # Show final migration status
        logger.info("Migration completed. Final status:")
        command.current(alembic_cfg)

        logger.info("✅ Database migrations completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False


def validate_post_migration():
    """Validate database state after migration."""
    try:
        logger.info("Validating post-migration database state...")

        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            # Basic connectivity test
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

            # Verify core tables exist
            tables_query = text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            )

            tables = conn.execute(tables_query).fetchall()
            table_names = [row[0] for row in tables]

            expected_tables = [
                "sessions",
                "activities",
                "participants",
                "user_responses",
                "alembic_version",
            ]

            for table in expected_tables:
                if table not in table_names:
                    raise Exception(f"Expected table '{table}' not found")

            logger.info(
                f"✅ Database validation passed. Found {len(table_names)} tables."
            )
            return True

    except Exception as e:
        logger.error(f"❌ Post-migration validation failed: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("=== Database Migration Runner ===")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database URL: {settings.database_url.split('@')[0]}@[REDACTED]")

    # Run migrations
    migration_success = run_migrations()

    if migration_success:
        # Validate the migration
        validation_success = validate_post_migration()

        if validation_success:
            logger.info("🎉 Migration and validation completed successfully!")
            sys.exit(0)
        else:
            logger.error("💥 Migration completed but validation failed!")
            sys.exit(1)
    else:
        logger.error("💥 Migration failed!")
        sys.exit(1)
