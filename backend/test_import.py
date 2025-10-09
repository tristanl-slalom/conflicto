#!/usr/bin/env python3
"""Simple script to test imports and find issues."""

print("Starting import test...")

try:
    print("1. Testing enum imports...")
    from app.db.enums import ActivityType, ParticipantRole

    print("   ✓ Enums imported successfully")

    print("2. Testing schema imports...")
    from app.models.schemas import SessionCreate, ActivityCreate, ParticipantCreate

    print("   ✓ Schemas imported successfully")

    print("3. Testing Pydantic model creation...")
    session_create = SessionCreate(title="Test Session", description="Test")
    print("   ✓ SessionCreate model created")

    activity_create = ActivityCreate(
        title="Test Activity",
        activity_type=ActivityType.POLL,
        description="Test activity",
    )
    print("   ✓ ActivityCreate model created")

    participant_create = ParticipantCreate(
        display_name="Test User", role=ParticipantRole.PARTICIPANT
    )
    print("   ✓ ParticipantCreate model created")

    print("4. Testing model serialization...")
    print(f"   Activity type: {activity_create.activity_type}")
    print(f"   Participant role: {participant_create.role}")

    print("\n✅ ALL TESTS PASSED!")

except Exception as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    import traceback

    traceback.print_exc()
