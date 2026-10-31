"""Auth schemas — registration, login, token response."""
import re
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class RegisterRequest(BaseModel):
    """Payload for POST /api/auth/register."""

    email: EmailStr
    password: str
    full_name: str
    role: str = "customer"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("must contain an uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("must contain a lowercase letter")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("must contain a special character")
        return v

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str) -> str:
        allowed = ("admin", "staff", "customer")
        if v not in allowed:
            raise ValueError(f"must be one of: {', '.join(allowed)}")
        return v


class LoginRequest(BaseModel):
    """Payload for POST /api/auth/login."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Public user data returned after auth operations."""

    id: int
    email: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Access token returned on successful login."""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
