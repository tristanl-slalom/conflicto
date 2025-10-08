"""Test basic functionality to debug issues."""


def test_simple():
    """Test that basic testing works."""
    assert 1 + 1 == 2


def test_imports():
    """Test that we can import our modules."""
    from app.db.enums import ActivityStatus

    assert ActivityStatus.DRAFT == "draft"
