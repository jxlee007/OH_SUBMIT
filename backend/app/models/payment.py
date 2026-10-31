"""Payment model — must be positive, linked to one invoice."""
from sqlalchemy import Column, String, Numeric, Integer, Date, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import IDMixin, TimestampMixin


class Payment(IDMixin, TimestampMixin, Base):
    """A payment recorded against a confirmed or paid invoice."""

    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payment_positive"),
    )

    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    method = Column(String(50), nullable=False, default="bank_transfer")
    payment_date = Column(Date, nullable=False)
    reference = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments", lazy="joined")
