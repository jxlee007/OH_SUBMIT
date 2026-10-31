"""Subscription and SubscriptionLine models."""
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Integer, Date, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import IDMixin, TimestampMixin

SUBSCRIPTION_STATUS = ("draft", "confirmed", "active", "closed")

# Valid status transitions
STATUS_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["confirmed", "closed"],
    "confirmed": ["active", "closed"],
    "active": ["closed"],
    "closed": [],
}


class Subscription(IDMixin, TimestampMixin, Base):
    """A customer subscription to a plan."""

    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'confirmed', 'active', 'closed')",
            name="ck_subscription_status",
        ),
    )

    number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    payment_terms = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    notes = Column(Text, nullable=True)

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], lazy="joined")
    plan = relationship("Plan", back_populates="subscriptions", lazy="joined")
    lines = relationship("SubscriptionLine", back_populates="subscription", lazy="select", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="subscription", lazy="select")


class SubscriptionLine(IDMixin, Base):
    """A single product line within a subscription."""

    __tablename__ = "subscription_lines"

    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    description = Column(String(500), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(12, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    amount = Column(Numeric(12, 2), nullable=False)

    # Relationships
    subscription = relationship("Subscription", back_populates="lines")
    product = relationship("Product", lazy="joined")
