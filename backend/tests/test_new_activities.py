"""Tests for New Activity operations and JSONB configuration."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NewActivity, ActivityStatus

pytestmark = pytest.mark.asyncio


class TestNewActivities:
    """Test cases for New Activity JSONB configuration operations."""

    async def test_create_activity_with_jsonb_config(
        self, async_client: AsyncClient, test_session
    ):
        """Test creating an activity with JSONB configuration."""
        activity_data = {
            "type": "planning_poker",
            "config": {
                "version": "1.0",
                "settings": {
                    "cards": [1, 2, 3, 5, 8, 13, 21],
                    "timer": 300,
                    "allow_revotes": True
                },
                "display": {
                    "title": "Sprint Planning - User Stories",
                    "description": "Estimate story points for user stories",
                    "instructions": "Select a card that represents your estimate"
                },
                "constraints": {
                    "time_limit": 300,
                    "max_responses": 1,
                    "allow_changes": True
                }
            },
            "order_index": 1
        }
        
        response = await async_client.post(
            f"/api/v1/sessions/{test_session.id}/activities",
            json=activity_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "planning_poker"
        assert data["config"]["settings"]["cards"] == [1, 2, 3, 5, 8, 13, 21]
        assert data["config"]["settings"]["timer"] == 300
        assert data["config"]["display"]["title"] == "Sprint Planning - User Stories"

    async def test_get_session_activities(
        self, async_client: AsyncClient, test_session
    ):
        """Test retrieving all activities for a session."""
        response = await async_client.get(f"/api/v1/sessions/{test_session.id}/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        assert "total_count" in data
        assert isinstance(data["activities"], list)

    async def test_get_activity_by_id(
        self, async_client: AsyncClient, test_new_activity
    ):
        """Test getting a specific activity by ID."""
        response = await async_client.get(f"/api/v1/activities/{test_new_activity.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_new_activity.id)
        assert data["type"] == test_new_activity.type

    async def test_update_activity_config(
        self, async_client: AsyncClient, test_new_activity
    ):
        """Test updating activity configuration."""
        updated_config = {
            "config": {
                "version": "1.1",
                "settings": {
                    "cards": [1, 2, 3, 5, 8, 13],  # Updated cards
                    "timer": 600,  # Updated timer
                    "allow_revotes": False
                },
                "display": {
                    "title": "Updated Planning Session",
                    "description": "Updated description"
                }
            }
        }
        
        response = await async_client.put(
            f"/api/v1/activities/{test_new_activity.id}",
            json=updated_config,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["version"] == "1.1"
        assert data["config"]["settings"]["timer"] == 600
        assert data["config"]["settings"]["allow_revotes"] is False

    async def test_update_activity_status(
        self, async_client: AsyncClient, test_new_activity
    ):
        """Test updating activity status."""
        response = await async_client.patch(
            f"/api/v1/activities/{test_new_activity.id}/status?status=active"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    async def test_get_active_activity(
        self, async_client: AsyncClient, test_session
    ):
        """Test getting the currently active activity."""
        response = await async_client.get(
            f"/api/v1/sessions/{test_session.id}/activities/active"
        )
        
        assert response.status_code == 200
        # Response can be null if no active activity

    async def test_delete_activity(
        self, async_client: AsyncClient, test_new_activity
    ):
        """Test deleting an activity."""
        response = await async_client.delete(f"/api/v1/activities/{test_new_activity.id}")
        
        assert response.status_code == 204

    async def test_activity_ordering(
        self, async_client: AsyncClient, test_session
    ):
        """Test activity ordering by order_index."""
        # Create multiple activities with different order_index
        activities_data = [
            {"type": "poll", "config": {}, "order_index": 3},
            {"type": "word_cloud", "config": {}, "order_index": 1},
            {"type": "planning_poker", "config": {}, "order_index": 2},
        ]
        
        for activity_data in activities_data:
            response = await async_client.post(
                f"/api/v1/sessions/{test_session.id}/activities",
                json=activity_data,
            )
            assert response.status_code == 201
        
        # Get activities and verify ordering
        response = await async_client.get(f"/api/v1/sessions/{test_session.id}/activities")
        data = response.json()
        
        activities = data["activities"]
        if len(activities) >= 3:
            # Should be ordered by order_index
            assert activities[0]["order_index"] <= activities[1]["order_index"]
            assert activities[1]["order_index"] <= activities[2]["order_index"]


class TestActivityConfigJSONB:
    """Test cases for Activity JSONB configuration operations."""

    async def test_complex_config_structure(
        self, async_client: AsyncClient, test_session
    ):
        """Test creating activity with complex JSONB configuration."""
        complex_config = {
            "type": "word_cloud",
            "config": {
                "version": "2.0",
                "settings": {
                    "max_words": 50,
                    "min_word_length": 3,
                    "max_word_length": 20,
                    "banned_words": ["inappropriate", "spam"],
                    "categories": [
                        {"name": "Technology", "color": "#FF6B6B"},
                        {"name": "Process", "color": "#4ECDC4"},
                        {"name": "People", "color": "#45B7D1"}
                    ],
                    "scoring": {
                        "enable_voting": True,
                        "max_votes_per_word": 5,
                        "voting_algorithm": "weighted"
                    }
                },
                "display": {
                    "title": "Retrospective Word Cloud",
                    "description": "Share your thoughts on this sprint",
                    "instructions": "Enter words that describe your experience",
                    "theme": {
                        "background_color": "#F8F9FA",
                        "text_color": "#343A40",
                        "accent_color": "#007BFF"
                    }
                },
                "constraints": {
                    "time_limit": 600,
                    "max_responses": 5,
                    "allow_changes": True,
                    "require_moderation": False
                },
                "advanced": {
                    "nlp_processing": True,
                    "sentiment_analysis": True,
                    "auto_clustering": True,
                    "export_formats": ["png", "svg", "pdf"]
                }
            },
            "order_index": 1
        }
        
        response = await async_client.post(
            f"/api/v1/sessions/{test_session.id}/activities",
            json=complex_config,
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify complex structure is preserved
        config = data["config"]
        assert config["version"] == "2.0"
        assert len(config["settings"]["categories"]) == 3
        assert config["settings"]["scoring"]["enable_voting"] is True
        assert config["display"]["theme"]["background_color"] == "#F8F9FA"
        assert config["advanced"]["nlp_processing"] is True

    async def test_jsonb_query_on_config(
        self, db_session: AsyncSession, test_session
    ):
        """Test JSONB queries on activity configuration."""
        # Create activity with specific config
        activity = NewActivity(
            session_id=test_session.id,
            type="planning_poker",
            config={
                "version": "1.0",
                "settings": {
                    "timer": 300,
                    "cards": [1, 2, 3, 5, 8]
                }
            },
            order_index=1,
        )
        db_session.add(activity)
        await db_session.commit()
        
        # Query activities with specific config values
        from sqlalchemy import text
        query = text("""
            SELECT * FROM new_activities 
            WHERE session_id = :session_id
            AND config @> '{"settings": {"timer": 300}}'
        """)
        
        result = await db_session.execute(
            query, 
            {"session_id": test_session.id}
        )
        found_activities = result.fetchall()
        
        assert len(found_activities) >= 1

    async def test_config_json_path_extraction(
        self, db_session: AsyncSession, test_new_activity
    ):
        """Test JSON path extraction from activity configuration."""
        from sqlalchemy import text
        
        # Extract specific config values using JSON operators
        query = text("""
            SELECT 
                config->'settings'->>'timer' as timer,
                config->'display'->>'title' as title,
                config->'version' as version
            FROM new_activities 
            WHERE id = :activity_id
        """)
        
        result = await db_session.execute(
            query, 
            {"activity_id": test_new_activity.id}
        )
        row = result.fetchone()
        
        # Verify extraction works
        assert row is not None

    async def test_config_validation_patterns(
        self, async_client: AsyncClient, test_session
    ):
        """Test various configuration patterns and edge cases."""
        test_configs = [
            # Minimal config
            {"type": "simple", "config": {}, "order_index": 1},
            
            # Config with nested arrays
            {
                "type": "multi_choice",
                "config": {
                    "options": [
                        {"id": 1, "text": "Option A", "metadata": {"color": "red"}},
                        {"id": 2, "text": "Option B", "metadata": {"color": "blue"}}
                    ]
                },
                "order_index": 2
            },
            
            # Config with deep nesting
            {
                "type": "complex",
                "config": {
                    "level1": {
                        "level2": {
                            "level3": {
                                "deep_value": "test",
                                "array": [1, 2, 3]
                            }
                        }
                    }
                },
                "order_index": 3
            }
        ]
        
        for config in test_configs:
            response = await async_client.post(
                f"/api/v1/sessions/{test_session.id}/activities",
                json=config,
            )
            assert response.status_code == 201
            
            # Verify config structure is preserved
            data = response.json()
            assert data["config"] == config["config"]


class TestJSONBPerformance:
    """Test cases for JSONB performance with activity configurations."""

    async def test_large_config_storage(
        self, async_client: AsyncClient, test_session
    ):
        """Test storing large activity configurations."""
        large_config = {
            "type": "comprehensive_survey",
            "config": {
                "questions": [
                    {
                        "id": i,
                        "type": "multiple_choice",
                        "text": f"Question {i}",
                        "options": [f"Option {j}" for j in range(10)],
                        "metadata": {f"key_{k}": f"value_{k}" for k in range(20)}
                    }
                    for i in range(100)  # 100 questions
                ],
                "settings": {f"setting_{i}": f"value_{i}" for i in range(50)},
                "large_text_field": "x" * 5000  # 5KB of text
            },
            "order_index": 1
        }
        
        response = await async_client.post(
            f"/api/v1/sessions/{test_session.id}/activities",
            json=large_config,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["config"]["questions"]) == 100

    async def test_config_index_performance(
        self, db_session: AsyncSession, test_session
    ):
        """Test performance of JSONB queries with GIN indexes."""
        # Create multiple activities with varied configs
        for i in range(50):
            activity = NewActivity(
                session_id=test_session.id,
                type=f"type_{i % 5}",
                config={
                    "category": f"cat_{i % 10}",
                    "settings": {"value": i, "enabled": i % 2 == 0},
                    "metadata": {"created": f"2025-10-{7 + (i % 20)}", "priority": i % 3}
                },
                order_index=i,
            )
            db_session.add(activity)
        
        await db_session.commit()
        
        # Test complex JSONB query performance
        from sqlalchemy import text
        query = text("""
            SELECT COUNT(*) 
            FROM new_activities 
            WHERE session_id = :session_id
            AND config @> '{"settings": {"enabled": true}}'
            AND config->'metadata'->>'priority' = '1'
        """)
        
        result = await db_session.execute(
            query, 
            {"session_id": test_session.id}
        )
        count = result.scalar()
        
        # Verify query executed successfully
        assert count >= 0