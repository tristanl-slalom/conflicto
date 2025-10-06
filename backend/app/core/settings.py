"""
Core configuration settings for the Caja backend application.
"""
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # CORS
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        env="ALLOWED_ORIGINS"
    )
    
    # Polling
    polling_interval_seconds: int = Field(default=2, env="POLLING_INTERVAL_SECONDS")
    
    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Caja Backend"
    version: str = "0.1.0"
    
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    @property
    def allowed_origins(self) -> List[str]:
        """Parse comma-separated allowed origins."""
        return [origin.strip() for origin in self.allowed_origins_str.split(",")]


# Global settings instance
settings = Settings()