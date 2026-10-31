"""Discount rules model — supports percentage and fixed discounts across subscriptions or products."""
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Integer, Date, Boolean, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import IDMixin, TimestampMixin


class DiscountRule(IDMixin, TimestampMixin, Base):
    """Discount rule applied during invoice generation."""

    __tablename__ = "discount_rules"
    __table_args__ = (
        CheckConstraint(
            "rule_type IN ('fixed', 'percent')",
            name="ck_discount_rule_type",
        ),
        CheckConstraint(
            "applies_to IN ('subscription', 'product')",
            name="ck_discount_applies_to",
        ),
        CheckConstraint(
            "discount_value > 0",
            name="ck_discount_value_positive",
        ),
        CheckConstraint(
            "rule_type != 'percent' OR discount_value <= 100",
            name="ck_discount_percent_max",
        ),
        CheckConstraint(
            "times_used >= 0",
            name="ck_discount_times_used_non_negative",
        ),
        CheckConstraint(
            "usage_limit IS NULL OR usage_limit >= 0",
            name="ck_discount_usage_limit_non_negative",
        ),
    )

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    rule_type = Column(String(20), nullable=False)  # "fixed" or "percent"
    discount_value = Column(Numeric(10, 2), nullable=False)
    applies_to = Column(String(20), default="subscription", nullable=False)  # "subscription" or "product"
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)

    min_amount = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    min_quantity = Column(Integer, default=0, nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=False)
    usage_limit = Column(Integer, nullable=True)  # None = unlimited
    times_used = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship
    product = relationship("Product", lazy="joined")
