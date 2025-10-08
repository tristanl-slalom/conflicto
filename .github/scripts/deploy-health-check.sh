#!/bin/bash
set -e

# Health check script for deployment validation
# Usage: ./deploy-health-check.sh <base_url> [timeout_seconds]

BASE_URL="${1:-http://localhost:8000}"
TIMEOUT="${2:-60}"
HEALTH_ENDPOINT="${BASE_URL}/health"

echo "🔍 Starting health check for ${BASE_URL}"
echo "⏰ Timeout: ${TIMEOUT} seconds"

start_time=$(date +%s)
end_time=$((start_time + TIMEOUT))

# Function to check health endpoint
check_health() {
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH_ENDPOINT}" 2>/dev/null || echo "000")
    echo "$response"
}

# Wait for service to be healthy
echo "🔄 Waiting for service to become healthy..."

while [ $(date +%s) -lt $end_time ]; do
    http_code=$(check_health)

    if [ "$http_code" = "200" ]; then
        echo "✅ Service is healthy! (HTTP $http_code)"

        # Additional checks for more comprehensive validation
        echo "🔍 Running additional health checks..."

        # Check if response contains expected health data
        health_response=$(curl -s "${HEALTH_ENDPOINT}")

        if echo "$health_response" | grep -q "status"; then
            echo "✅ Health endpoint returns valid JSON response"
        else
            echo "⚠️ Health endpoint response may be invalid"
            echo "Response: $health_response"
        fi

        # Check response time
        response_time=$(curl -s -o /dev/null -w "%{time_total}" "${HEALTH_ENDPOINT}")
        echo "📊 Response time: ${response_time}s"

        if [ $(echo "$response_time < 2.0" | bc -l) -eq 1 ]; then
            echo "✅ Response time is acceptable"
        else
            echo "⚠️ Response time is slow (>${response_time}s)"
        fi

        echo "🎉 Health check completed successfully!"
        exit 0
    else
        echo "⏳ Service not ready (HTTP $http_code), retrying in 5 seconds..."
        sleep 5
    fi
done

echo "❌ Health check timed out after ${TIMEOUT} seconds"
echo "🔍 Final attempt - detailed curl output:"
curl -v "${HEALTH_ENDPOINT}" || true

exit 1
