"""
Core configuration settings for the Caja backend application.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = Field(..., description="Database URL for PostgreSQL")

    # Security
    secret_key: str = Field(..., description="Secret key for JWT token signing")
    algorithm: str = Field(
        default="HS256", description="Algorithm for JWT token signing"
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )

    # Environment
    environment: str = Field(
        default="development", description="Application environment"
    )
    debug: bool = Field(default=False, description="Debug mode flag")

    # Deployment
    app_version: str = Field(
        default="unknown", description="Application version (usually git commit SHA)"
    )
    aws_region: str = Field(
        default="us-west-2", description="AWS region for deployment"
    )

    # CORS
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        description="Allowed CORS origins",
    )

    # Polling
    polling_interval_seconds: int = Field(
        default=2, description="Polling interval in seconds"
    )

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Caja Backend"
    version: str = "0.1.0"

    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    @property
    def allowed_origins(self) -> list[str]:
        """Parse comma-separated allowed origins."""
        return [origin.strip() for origin in self.allowed_origins_str.split(",")]


# Global settings instance
settings = Settings()
