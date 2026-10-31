"""Base models and shared model mixins."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, text
from backend.app.core.database import Base


class TimestampMixin:
    """Mixin providing created_at / updated_at audit columns."""

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )


class IDMixin:
    """Mixin providing a surrogate integer primary key."""

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
