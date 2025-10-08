#!/usr/bin/env python3
"""
Health check validation script for deployment pipeline.

Validates that the deployed application is healthy and ready to serve traffic.
"""

import asyncio
import logging
import sys
from urllib.parse import urljoin

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_health_endpoint(base_url: str, timeout: int = 30) -> bool:
    """Check the health endpoint of the application."""
    health_url = urljoin(base_url, "/api/v1/health/")

    logger.info(f"Checking health endpoint: {health_url}")

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(health_url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Health check passed: {data}")

                # Validate response structure
                required_fields = ["status", "version"]
                for field in required_fields:
                    if field not in data:
                        logger.error(f"❌ Missing required field: {field}")
                        return False

                if data["status"] != "healthy":
                    logger.error(
                        f"❌ Service reports unhealthy status: {data['status']}"
                    )
                    return False

                return True
            else:
                logger.error(
                    f"❌ Health check failed with status {response.status_code}: {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Health check failed with exception: {str(e)}")
            return False


async def check_readiness_endpoint(base_url: str, timeout: int = 30) -> bool:
    """Check the readiness endpoint of the application."""
    ready_url = urljoin(base_url, "/api/v1/health/ready")

    logger.info(f"Checking readiness endpoint: {ready_url}")

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(ready_url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Readiness check passed: {data}")
                return True
            else:
                logger.error(
                    f"❌ Readiness check failed with status {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Readiness check failed with exception: {str(e)}")
            return False


async def wait_for_service(
    base_url: str, max_attempts: int = 30, delay: int = 5
) -> bool:
    """Wait for the service to become healthy with retries."""
    logger.info(f"Waiting for service at {base_url} to become healthy...")
    logger.info(f"Max attempts: {max_attempts}, Delay between attempts: {delay}s")

    for attempt in range(1, max_attempts + 1):
        logger.info(f"Attempt {attempt}/{max_attempts}")

        health_ok = await check_health_endpoint(base_url)
        ready_ok = await check_readiness_endpoint(base_url)

        if health_ok and ready_ok:
            logger.info(f"🎉 Service is healthy after {attempt} attempts!")
            return True

        if attempt < max_attempts:
            logger.info(f"Service not ready, waiting {delay}s before next attempt...")
            await asyncio.sleep(delay)

    logger.error(f"❌ Service failed to become healthy after {max_attempts} attempts")
    return False


async def run_smoke_tests(base_url: str) -> bool:
    """Run basic smoke tests against the deployed application."""
    logger.info("Running smoke tests...")

    # Test cases for smoke tests
    test_cases = [
        {"name": "Health Endpoint", "url": "/api/v1/health/", "expected_status": 200},
        {
            "name": "Readiness Endpoint",
            "url": "/api/v1/health/ready",
            "expected_status": 200,
        },
        {
            "name": "Liveness Endpoint",
            "url": "/api/v1/health/live",
            "expected_status": 200,
        },
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        all_passed = True

        for test_case in test_cases:
            test_url = urljoin(base_url, test_case["url"])
            logger.info(f"Testing {test_case['name']}: {test_url}")

            try:
                response = await client.get(test_url)

                if response.status_code == test_case["expected_status"]:
                    logger.info(f"✅ {test_case['name']} passed")
                else:
                    logger.error(
                        f"❌ {test_case['name']} failed: expected {test_case['expected_status']}, got {response.status_code}"
                    )
                    all_passed = False

            except Exception as e:
                logger.error(f"❌ {test_case['name']} failed with exception: {str(e)}")
                all_passed = False

        return all_passed


async def main():
    """Main health check function."""
    import os

    # Get base URL from environment or use default
    base_url = os.getenv("HEALTH_CHECK_URL", "http://localhost:8000")
    max_attempts = int(os.getenv("HEALTH_CHECK_MAX_ATTEMPTS", "30"))
    delay = int(os.getenv("HEALTH_CHECK_DELAY", "5"))

    logger.info("=== Deployment Health Check ===")
    logger.info(f"Target URL: {base_url}")
    logger.info(f"Max attempts: {max_attempts}")
    logger.info(f"Delay between attempts: {delay}s")

    # Wait for service to become healthy
    service_ready = await wait_for_service(base_url, max_attempts, delay)

    if not service_ready:
        logger.error("💥 Service failed to become healthy!")
        sys.exit(1)

    # Run smoke tests
    smoke_tests_passed = await run_smoke_tests(base_url)

    if smoke_tests_passed:
        logger.info("🎉 All health checks and smoke tests passed!")
        sys.exit(0)
    else:
        logger.error("💥 Smoke tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
