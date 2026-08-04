"""
Pydantic schemas for user profile endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ProfileResponse(BaseModel):
    """GET /profile response body — never includes password_hash."""
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    """PUT /profile request body — all fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)
