"""User model — authentication and role management."""
from sqlalchemy import Column, String, CheckConstraint
from backend.app.core.database import Base
from backend.app.models.base import IDMixin, TimestampMixin

ROLE_VALUES = ("admin", "staff", "customer")


class User(IDMixin, TimestampMixin, Base):
    """Application user with role-based access control."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'staff', 'customer')",
            name="ck_user_role",
        ),
    )

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="customer")
    is_active = Column(String(1), nullable=False, default="Y")
