"""Minimal test configuration to debug import issues"""
import pytest
import os

# Set test environment variables first
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ENVIRONMENT"] = "testing"

def test_simple():
    """Simple test that should always pass"""
    assert 1 + 1 == 2

def test_activity_status_import():
    """Test ActivityStatus enum import"""
    from app.db.enums import ActivityStatus
    assert ActivityStatus.DRAFT == "draft"
    assert ActivityStatus.ACTIVE == "active"