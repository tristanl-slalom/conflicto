"""
Integration tests for deployed Conflicto environments.

These tests run against live deployed environments to validate
end-to-end functionality after deployment.
"""

import asyncio
import os
import pytest
import httpx
from datetime import datetime

# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
TIMEOUT = 30


class TestDeployedEnvironment:
    """Test suite for deployed environment validation."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test basic health endpoint."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/v1/health/")

            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "healthy"
            assert "version" in data
            assert "timestamp" in data

            # Validate deployment-specific fields if present
            if "environment" in data:
                assert data["environment"] in ["dev", "prod", "development"]

            if "app_version" in data:
                assert isinstance(data["app_version"], str)

    @pytest.mark.asyncio
    async def test_readiness_endpoint(self):
        """Test readiness endpoint."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/v1/health/ready")

            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "ready"

    @pytest.mark.asyncio
    async def test_liveness_endpoint(self):
        """Test liveness endpoint."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/v1/health/live")

            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "alive"

    @pytest.mark.asyncio
    async def test_database_connectivity(self):
        """Test database connectivity through health endpoint."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/v1/health/")

            assert response.status_code == 200

            # If the health endpoint returns 200, the database connection is working
            # (health endpoint tests database connectivity internally)
            data = response.json()
            assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_session_api_endpoints(self):
        """Test core session API functionality."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test session creation
            session_data = {
                "name": "Integration Test Session",
                "description": "Test session for deployment validation",
            }

            response = await client.post(
                f"{BASE_URL}/api/v1/sessions/", json=session_data
            )
            assert response.status_code == 201

            session = response.json()
            assert "id" in session
            assert session["name"] == session_data["name"]
            assert session["status"] == "draft"

            session_id = session["id"]

            # Test session retrieval
            response = await client.get(f"{BASE_URL}/api/v1/sessions/{session_id}")
            assert response.status_code == 200

            retrieved_session = response.json()
            assert retrieved_session["id"] == session_id
            assert retrieved_session["name"] == session_data["name"]

            # Test session list
            response = await client.get(f"{BASE_URL}/api/v1/sessions/")
            assert response.status_code == 200

            sessions = response.json()
            assert isinstance(sessions, list)

            # Find our test session
            test_session = next((s for s in sessions if s["id"] == session_id), None)
            assert test_session is not None

            # Cleanup - delete test session
            response = await client.delete(f"{BASE_URL}/api/v1/sessions/{session_id}")
            assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_cors_headers(self):
        """Test CORS headers are properly configured."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test preflight request
            headers = {
                "Origin": "https://conflicto.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            }

            response = await client.options(
                f"{BASE_URL}/api/v1/sessions/", headers=headers
            )

            # Should allow the request (either 200 or 204)
            assert response.status_code in [200, 204]

    @pytest.mark.asyncio
    async def test_response_times(self):
        """Test that response times are acceptable."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            start_time = datetime.now()

            response = await client.get(f"{BASE_URL}/api/v1/health/")

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()

            assert response.status_code == 200
            assert (
                response_time < 2.0
            )  # Health endpoint should respond within 2 seconds

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid requests."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test 404 for non-existent session
            response = await client.get(f"{BASE_URL}/api/v1/sessions/99999")
            assert response.status_code == 404

            # Test 422 for invalid session data
            invalid_session_data = {"name": ""}  # Empty name should be invalid
            response = await client.post(
                f"{BASE_URL}/api/v1/sessions/", json=invalid_session_data
            )
            assert response.status_code == 422


class TestPerformance:
    """Performance validation tests for deployed environment."""

    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self):
        """Test concurrent health check requests."""

        async def health_check():
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(f"{BASE_URL}/api/v1/health/")
                return response.status_code == 200

        # Run 10 concurrent health checks
        tasks = [health_check() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(results)

    @pytest.mark.asyncio
    async def test_session_creation_performance(self):
        """Test session creation performance under load."""

        async def create_session(index: int):
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                session_data = {
                    "name": f"Perf Test Session {index}",
                    "description": f"Performance test session {index}",
                }

                start_time = datetime.now()
                response = await client.post(
                    f"{BASE_URL}/api/v1/sessions/", json=session_data
                )
                end_time = datetime.now()

                response_time = (end_time - start_time).total_seconds()

                # Cleanup
                if response.status_code == 201:
                    session_id = response.json()["id"]
                    await client.delete(f"{BASE_URL}/api/v1/sessions/{session_id}")

                return {
                    "success": response.status_code == 201,
                    "response_time": response_time,
                }

        # Create 5 sessions concurrently
        tasks = [create_session(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(result["success"] for result in results)

        # Average response time should be reasonable
        avg_response_time = sum(result["response_time"] for result in results) / len(
            results
        )
        assert avg_response_time < 3.0  # Average should be under 3 seconds


if __name__ == "__main__":
    print(f"Running integration tests against: {BASE_URL}")
    pytest.main([__file__, "-v"])
