"""Product model — distinct 3NF entity for sellable products and services."""
from sqlalchemy import Column, String, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import IDMixin, TimestampMixin
# Import Plan so that relationship("Plan", ...) resolves cleanly
from backend.app.models.plan import Plan  # noqa: F401


class Product(IDMixin, TimestampMixin, Base):
    """A sellable base product or service in the catalog."""

    __tablename__ = "products"

    name = Column(String(255), nullable=False)
    product_type = Column(String(100), nullable=False, default="service")
    sales_price = Column(Numeric(12, 2), nullable=False, default=0)
    cost_price = Column(Numeric(12, 2), nullable=False, default=0)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships (1 Product has many Plans)
    plans = relationship("Plan", back_populates="product", lazy="select")
