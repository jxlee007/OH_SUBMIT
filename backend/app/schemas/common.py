"""Shared Pydantic schemas and standard response envelopes."""
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    """Standardized API response envelope adhering to Level 7 architecture."""
    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None

class HealthStatus(BaseModel):
    """Health check status schema."""
    status: str
    database: dict[str, Any]
    version: str

