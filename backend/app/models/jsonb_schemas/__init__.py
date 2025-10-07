"""Schema models for the API."""

# Import existing schemas from parent schemas.py
from ..schemas import ErrorResponse, HealthResponse

# Import new JSONB schemas
from .new_activity import *
from .user_response import *