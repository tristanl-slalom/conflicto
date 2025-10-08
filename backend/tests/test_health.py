"""
Tests for health check API endpoints.
"""
from httpx import AsyncClient


class TestHealthAPI:
    """Test health check API endpoints."""

    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/api/v1/health/")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["version"] == "0.1.0"

    async def test_readiness_check(self, async_client: AsyncClient):
        """Test readiness check endpoint."""
        response = await async_client.get("/api/v1/health/ready")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ready"
        assert data["version"] == "0.1.0"

    async def test_liveness_check(self, async_client: AsyncClient):
        """Test liveness check endpoint."""
        response = await async_client.get("/api/v1/health/live")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "alive"
        assert data["version"] == "0.1.0"
