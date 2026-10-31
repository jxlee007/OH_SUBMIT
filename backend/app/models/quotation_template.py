"""Quotation templates and template lines models."""
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Integer, Text, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import IDMixin, TimestampMixin


class QuotationTemplate(IDMixin, TimestampMixin, Base):
    """Quotation template representing standard recurring bundles."""

    __tablename__ = "quotation_templates"
    __table_args__ = (
        CheckConstraint(
            "validity_days > 0",
            name="ck_quotation_template_validity_days_positive",
        ),
    )

    name = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="SET NULL"), nullable=True)
    validity_days = Column(Integer, default=30, nullable=False)

    # Relationships
    plan = relationship("Plan", lazy="joined")
    lines = relationship("QuotationTemplateLine", back_populates="template", cascade="all, delete-orphan", lazy="selectin")


class QuotationTemplateLine(IDMixin, Base):
    """Line items pre-configured in a quotation template."""

    __tablename__ = "quotation_template_lines"
    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_quotation_template_line_quantity_positive",
        ),
    )

    template_id = Column(Integer, ForeignKey("quotation_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), default=Decimal("18.00"), nullable=False)

    # Relationships
    template = relationship("QuotationTemplate", back_populates="lines")
    product = relationship("Product", lazy="joined")
