#!/usr/bin/env python3
"""Debug script for activity creation issues."""
import asyncio
import httpx
from sqlalchemy import text
from app.db.database import get_db


async def debug_activity_creation():
    """Debug activity creation endpoint."""
    
    # First create a session
    session_data = {
        "title": "Debug Session",
        "description": "Test session for debugging",
        "max_participants": 50
    }
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        print("1. Creating session...")
        session_response = await client.post("/api/v1/sessions/", json=session_data)
        print(f"   Status: {session_response.status_code}")
        print(f"   Content: {session_response.text}")
        
        if session_response.status_code != 201:
            print("❌ Failed to create session")
            return
        
        session = session_response.json()
        session_id = session["id"]
        print(f"✅ Session created: {session_id}")
        
        # Now create an activity
        activity_data = {
            "type": "poll",
            "config": {"question": "Debug question?", "options": ["A", "B"]},
            "order_index": 1,
            "status": "draft"
        }
        
        print(f"\n2. Creating activity for session {session_id}...")
        activity_response = await client.post(
            f"/api/v1/sessions/{session_id}/activities/",
            json=activity_data
        )
        
        print(f"   Status: {activity_response.status_code}")
        print(f"   Headers: {dict(activity_response.headers)}")
        print(f"   Content: '{activity_response.text}'")
        print(f"   Content length: {len(activity_response.text)}")
        
        if activity_response.status_code == 201 and activity_response.text:
            try:
                activity = activity_response.json()
                print(f"✅ Activity created: {activity}")
            except Exception as e:
                print(f"❌ Failed to parse JSON: {e}")
        else:
            print(f"❌ Failed to create activity")


if __name__ == "__main__":
    asyncio.run(debug_activity_creation())