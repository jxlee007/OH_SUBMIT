"""Invoice and InvoiceLine models — with double-billing guard."""
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Integer, Date, ForeignKey, CheckConstraint, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import IDMixin, TimestampMixin

INVOICE_STATUS = ("draft", "confirmed", "paid", "cancelled")

INVOICE_STATUS_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["confirmed", "cancelled"],
    "confirmed": ["paid", "cancelled"],
    "paid": [],
    "cancelled": [],
}


class Invoice(IDMixin, TimestampMixin, Base):
    """Invoice generated from a subscription for one billing period."""

    __tablename__ = "invoices"
    __table_args__ = (
        # Double-billing guard: one invoice per subscription per billing period key
        UniqueConstraint(
            "subscription_id",
            "billing_period_key",
            name="uq_invoice_subscription_period",
        ),
        CheckConstraint(
            "status IN ('draft', 'confirmed', 'paid', 'cancelled')",
            name="ck_invoice_status",
        ),
    )

    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="RESTRICT"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    # e.g. "2026-10" for monthly, "2026-W44" for weekly, "2026-365" for daily, "2026" for yearly
    billing_period_key = Column(String(20), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    tax_amount = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    total = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    due_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    notes = Column(Text, nullable=True)

    # Relationships
    subscription = relationship("Subscription", back_populates="invoices", lazy="joined")
    customer = relationship("User", foreign_keys=[customer_id], lazy="joined")
    lines = relationship("InvoiceLine", back_populates="invoice", lazy="select", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", lazy="select")


class InvoiceLine(IDMixin, Base):
    """A single product line on an invoice."""

    __tablename__ = "invoice_lines"
    __table_args__ = (
        CheckConstraint(
            "discount_amount >= 0",
            name="ck_invoice_line_discount_amount",
        ),
    )

    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=True)
    description = Column(String(500), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(12, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    discount_amount = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    net_amount = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    amount = Column(Numeric(12, 2), nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="lines")
    product = relationship("Product", lazy="joined")
