"""Product Attributes and Variants models."""
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import IDMixin, TimestampMixin


class ProductAttribute(IDMixin, TimestampMixin, Base):
    """Product attribute definition, e.g., 'Hosting Region', 'User Tier'."""

    __tablename__ = "product_attributes"

    name = Column(String(60), unique=True, nullable=False, index=True)

    # Relationships
    values = relationship("ProductAttributeValue", back_populates="attribute", cascade="all, delete-orphan", lazy="selectin")


class ProductAttributeValue(IDMixin, Base):
    """Specific values for an attribute, e.g., 'US-East', 'EU-Central', 'Enterprise'."""

    __tablename__ = "product_attribute_values"

    attribute_id = Column(Integer, ForeignKey("product_attributes.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(String(60), nullable=False)

    # Relationships
    attribute = relationship("ProductAttribute", back_populates="values")


class ProductVariant(IDMixin, TimestampMixin, Base):
    """Product variant with SKU and price delta differential."""

    __tablename__ = "product_variants"

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku = Column(String(60), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    price_delta = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    product = relationship("Product", lazy="joined")
