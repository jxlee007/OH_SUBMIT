"""Password reset token model — single-use with SHA-256 hash storage."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import IDMixin


class PasswordResetToken(IDMixin, Base):
    """Password reset token entity."""

    __tablename__ = "password_reset_tokens"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    user = relationship("User", lazy="joined")
