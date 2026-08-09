"""
Pydantic schemas for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """POST /register request body."""
    name: str = Field(..., min_length=1, max_length=100, examples=["Ali Khan"])
    email: EmailStr = Field(..., examples=["ali@example.com"])
    password: str = Field(..., min_length=6, max_length=128, examples=["securepassword123"])


class LoginRequest(BaseModel):
    """POST /login request body."""
    email: EmailStr = Field(..., examples=["ali@example.com"])
    password: str = Field(..., min_length=1, examples=["securepassword123"])


class TokenResponse(BaseModel):
    """JWT token response returned after register/login."""
    access_token: str
    token_type: str = "bearer"
