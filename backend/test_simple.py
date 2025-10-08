#!/usr/bin/env python3
"""Simple test to check if imports work"""

def test_basic_imports():
    """Test basic imports work"""
    try:
        from app.db.enums import ActivityStatus
        print(f"✅ ActivityStatus import successful: {ActivityStatus.DRAFT}")
        
        from app.db.models import Activity
        print("✅ Activity model import successful")
        
        from app.services.activity_service import ActivityService  
        print("✅ ActivityService import successful")
        
        from app.main import app
        print("✅ FastAPI app import successful")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_imports()
    exit(0 if success else 1)