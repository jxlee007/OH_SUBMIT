"""Shared Pydantic schemas and standard response envelopes."""
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """Standardized API response envelope: {data, error}."""

    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None


class HealthStatus(BaseModel):
    """Health check status schema."""

    status: str
    database: dict[str, Any]
    version: str


def ok(data: Any, message: str = "OK") -> dict:
    """Convenience builder for successful responses."""
    return {"success": True, "data": data, "error": None, "message": message}


def err(error: str, message: str = "") -> dict:
    """Convenience builder for error responses."""
    return {"success": False, "data": None, "error": error, "message": message or error}
