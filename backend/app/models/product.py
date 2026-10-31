"""Product and Plan models."""
from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import IDMixin, TimestampMixin

BILLING_PERIOD_VALUES = ("daily", "weekly", "monthly", "yearly")


class Product(IDMixin, TimestampMixin, Base):
    """A sellable product or service."""

    __tablename__ = "products"

    name = Column(String(255), nullable=False)
    product_type = Column(String(100), nullable=False, default="service")
    sales_price = Column(Numeric(12, 2), nullable=False, default=0)
    cost_price = Column(Numeric(12, 2), nullable=False, default=0)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    plans = relationship("Plan", back_populates="product", lazy="select")


class Plan(IDMixin, TimestampMixin, Base):
    """A subscription plan linked to a product, with billing period."""

    __tablename__ = "plans"
    __table_args__ = (
        CheckConstraint(
            "billing_period IN ('daily', 'weekly', 'monthly', 'yearly')",
            name="ck_plan_billing_period",
        ),
    )

    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    billing_period = Column(String(20), nullable=False, default="monthly")
    min_quantity = Column(Integer, nullable=False, default=1)
    available_from = Column(Date, nullable=True)
    available_until = Column(Date, nullable=True)
    auto_close = Column(Boolean, nullable=False, default=False)
    can_pause = Column(Boolean, nullable=False, default=False)
    can_renew = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    product = relationship("Product", back_populates="plans")
    subscriptions = relationship("Subscription", back_populates="plan", lazy="select")
