"""Tests for User Response operations and JSONB functionality."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserResponse, NewActivity, ActivityStatus

pytestmark = pytest.mark.asyncio


class TestUserResponses:
    """Test cases for User Response JSONB operations."""

    async def test_create_user_response(
        self, async_client: AsyncClient, test_session, test_new_activity, test_participant
    ):
        """Test creating a user response with JSONB data."""
        response_data = {
            "response_data": {
                "type": "planning_poker",
                "version": "1.0",
                "data": {
                    "estimate": 5,
                    "confidence": "high",
                    "reasoning": "Based on similar features we've built"
                },
                "metadata": {
                    "client_timestamp": "2025-10-07T16:30:00Z",
                    "device_type": "mobile",
                    "user_agent": "Mozilla/5.0..."
                }
            }
        }
        
        response = await async_client.post(
            f"/api/v1/sessions/{test_session.id}/activities/{test_new_activity.id}/responses?participant_id={test_participant.id}",
            json=response_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["response_data"]["type"] == "planning_poker"
        assert data["response_data"]["data"]["estimate"] == 5
        assert data["response_data"]["data"]["confidence"] == "high"
        assert "metadata" in data["response_data"]

    async def test_get_activity_responses(
        self, async_client: AsyncClient, test_session, test_new_activity
    ):
        """Test retrieving activity responses with summary."""
        response = await async_client.get(
            f"/api/v1/sessions/{test_session.id}/activities/{test_new_activity.id}/responses"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "responses" in data
        assert "summary" in data
        assert "total_responses" in data["summary"]
        assert "unique_participants" in data["summary"]
        assert "last_updated" in data["summary"]

    async def test_get_participant_response(
        self, async_client: AsyncClient, test_session, test_new_activity, test_participant
    ):
        """Test getting a specific participant's response."""
        # First create a response
        response_data = {
            "response_data": {
                "type": "poll",
                "version": "1.0",
                "data": {"choice": "option_a"},
                "metadata": {"timestamp": "2025-10-07T16:30:00Z"}
            }
        }
        
        create_response = await async_client.post(
            f"/api/v1/sessions/{test_session.id}/activities/{test_new_activity.id}/responses?participant_id={test_participant.id}",
            json=response_data,
        )
        assert create_response.status_code == 201
        
        # Then retrieve it
        get_response = await async_client.get(
            f"/api/v1/sessions/{test_session.id}/activities/{test_new_activity.id}/responses/{test_participant.id}"
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["response_data"]["type"] == "poll"
        assert data["response_data"]["data"]["choice"] == "option_a"

    async def test_update_user_response(self, async_client: AsyncClient, test_user_response):
        """Test updating a user response."""
        updated_data = {
            "response_data": {
                "type": "planning_poker",
                "version": "1.0",
                "data": {
                    "estimate": 8,
                    "confidence": "medium",
                    "reasoning": "Updated estimate after team discussion"
                }
            }
        }
        
        response = await async_client.put(
            f"/api/v1/responses/{test_user_response.id}",
            json=updated_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response_data"]["data"]["estimate"] == 8
        assert data["response_data"]["data"]["confidence"] == "medium"

    async def test_delete_user_response(self, async_client: AsyncClient, test_user_response):
        """Test deleting a user response."""
        response = await async_client.delete(f"/api/v1/responses/{test_user_response.id}")
        
        assert response.status_code == 204

    async def test_jsonb_query_performance(self, db_session: AsyncSession, test_session, test_new_activity, test_participant):
        """Test JSONB query performance with indexes."""
        # Create multiple responses for performance testing
        responses = []
        for i in range(100):
            response = UserResponse(
                session_id=test_session.id,
                activity_id=test_new_activity.id,
                participant_id=test_participant.id,
                response_data={
                    "type": "performance_test",
                    "version": "1.0",
                    "data": {"value": i, "category": f"cat_{i % 10}"},
                    "metadata": {"test": True}
                }
            )
            responses.append(response)
            db_session.add(response)
        
        await db_session.commit()
        
        # Test JSONB containment query with GIN index
        from sqlalchemy import text
        query = text("""
            SELECT COUNT(*) FROM user_responses 
            WHERE session_id = :session_id 
            AND activity_id = :activity_id 
            AND response_data @> '{"type": "performance_test"}'
        """)
        
        result = await db_session.execute(
            query, 
            {"session_id": test_session.id, "activity_id": test_new_activity.id}
        )
        count = result.scalar()
        assert count == 100

    async def test_jsonb_json_path_queries(self, db_session: AsyncSession, test_user_response):
        """Test JSON path queries on JSONB data."""
        from sqlalchemy import text
        
        # Test JSON path extraction
        query = text("""
            SELECT response_data->'data'->>'estimate' as estimate
            FROM user_responses 
            WHERE id = :response_id
        """)
        
        result = await db_session.execute(query, {"response_id": test_user_response.id})
        estimate = result.scalar()
        
        # Assuming test_user_response has planning poker data
        assert estimate is not None

    async def test_complex_jsonb_aggregation(self, db_session: AsyncSession, test_session, test_new_activity):
        """Test complex JSONB aggregation queries."""
        # Create responses with different estimates
        estimates = [1, 2, 3, 5, 8, 13, 5, 8, 3, 5]
        for i, estimate in enumerate(estimates):
            response = UserResponse(
                session_id=test_session.id,
                activity_id=test_new_activity.id,
                participant_id=1,  # Using a dummy participant_id
                response_data={
                    "type": "planning_poker",
                    "version": "1.0",
                    "data": {"estimate": estimate},
                }
            )
            db_session.add(response)
        
        await db_session.commit()
        
        # Test aggregation query
        from sqlalchemy import text
        query = text("""
            SELECT 
                (response_data->'data'->>'estimate')::int as estimate,
                COUNT(*) as count
            FROM user_responses 
            WHERE session_id = :session_id 
            AND activity_id = :activity_id
            AND response_data->'type' = '"planning_poker"'
            GROUP BY response_data->'data'->>'estimate'
            ORDER BY estimate
        """)
        
        result = await db_session.execute(
            query, 
            {"session_id": test_session.id, "activity_id": test_new_activity.id}
        )
        results = result.fetchall()
        
        # Verify aggregation results
        estimate_counts = {row[0]: row[1] for row in results}
        assert estimate_counts[5] == 3  # 5 appears 3 times
        assert estimate_counts[8] == 2  # 8 appears 2 times


class TestJSONBValidation:
    """Test cases for JSONB data validation and constraints."""

    async def test_invalid_json_structure(self, async_client: AsyncClient, test_session, test_new_activity, test_participant):
        """Test handling of invalid JSON structure."""
        invalid_data = {
            "response_data": "not a json object"  # Invalid structure
        }
        
        response = await async_client.post(
            f"/api/v1/sessions/{test_session.id}/activities/{test_new_activity.id}/responses?participant_id={test_participant.id}",
            json=invalid_data,
        )
        
        # Should accept it since we're using flexible JSONB
        # In production, you might want schema validation
        assert response.status_code == 201

    async def test_empty_response_data(self, async_client: AsyncClient, test_session, test_new_activity, test_participant):
        """Test handling of empty response data."""
        empty_data = {
            "response_data": {}
        }
        
        response = await async_client.post(
            f"/api/v1/sessions/{test_session.id}/activities/{test_new_activity.id}/responses?participant_id={test_participant.id}",
            json=empty_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["response_data"] == {}

    async def test_large_jsonb_payload(self, async_client: AsyncClient, test_session, test_new_activity, test_participant):
        """Test handling of large JSONB payloads."""
        large_data = {
            "response_data": {
                "type": "word_cloud",
                "version": "1.0",
                "data": {
                    "words": [f"word_{i}" for i in range(1000)],  # Large array
                    "metadata": {f"key_{i}": f"value_{i}" for i in range(100)}  # Large object
                },
                "metadata": {
                    "large_field": "x" * 10000  # Large string
                }
            }
        }
        
        response = await async_client.post(
            f"/api/v1/sessions/{test_session.id}/activities/{test_new_activity.id}/responses?participant_id={test_participant.id}",
            json=large_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["response_data"]["data"]["words"]) == 1000


class TestPerformanceAndIndexes:
    """Test cases for JSONB performance and index usage."""

    async def test_gin_index_usage(self, db_session: AsyncSession):
        """Test that GIN indexes are being used for JSONB queries."""
        from sqlalchemy import text
        
        # Check if GIN indexes exist
        index_query = text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename IN ('user_responses', 'new_activities')
            AND indexdef LIKE '%gin%'
        """)
        
        result = await db_session.execute(index_query)
        indexes = result.fetchall()
        
        # Should have GIN indexes on JSONB columns
        gin_indexes = [idx for idx in indexes if 'gin' in idx[1].lower()]
        assert len(gin_indexes) >= 2  # At least for user_responses and activities

    async def test_query_plan_analysis(self, db_session: AsyncSession, test_session, test_new_activity):
        """Test query execution plans for JSONB operations."""
        from sqlalchemy import text
        
        # Test query plan for JSONB containment
        plan_query = text("""
            EXPLAIN (FORMAT JSON) 
            SELECT * FROM user_responses 
            WHERE session_id = :session_id 
            AND activity_id = :activity_id 
            AND response_data @> '{"type": "planning_poker"}'
        """)
        
        result = await db_session.execute(
            plan_query, 
            {"session_id": test_session.id, "activity_id": test_new_activity.id}
        )
        plan = result.scalar()
        
        # Verify the plan is reasonable (basic check)
        assert plan is not None
        assert isinstance(plan, list)