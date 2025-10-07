"""
Tests for health check API endpoints.
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthAPI:
    """Test health check API endpoints."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/api/v1/health/")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["version"] == "0.1.0"

    def test_readiness_check(self, client: TestClient):
        """Test readiness check endpoint."""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ready"
        assert data["version"] == "0.1.0"

    def test_liveness_check(self, client: TestClient):
        """Test liveness check endpoint."""
        response = client.get("/api/v1/health/live")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "alive"
        assert data["version"] == "0.1.0"
