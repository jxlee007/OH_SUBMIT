"""Service layer for product attributes and variants."""
from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models.product import Product
from backend.app.models.variant import ProductAttribute, ProductAttributeValue, ProductVariant
from backend.app.schemas.variant import ProductAttributeCreate, ProductVariantCreate


def create_attribute(db: Session, data: ProductAttributeCreate) -> ProductAttribute:
    """Create a new product attribute with optional initial values."""
    existing = db.query(ProductAttribute).filter(ProductAttribute.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product attribute '{data.name}' already exists",
        )

    attr = ProductAttribute(name=data.name)
    db.add(attr)
    db.flush()

    for val in data.values:
        val_record = ProductAttributeValue(attribute_id=attr.id, value=val)
        db.add(val_record)

    db.commit()
    db.refresh(attr)
    return attr


def list_attributes(db: Session) -> List[ProductAttribute]:
    """Retrieve all product attributes."""
    return db.query(ProductAttribute).order_by(ProductAttribute.id).all()


def create_variant(db: Session, data: ProductVariantCreate) -> ProductVariant:
    """Create a new product variant with SKU uniqueness and product existence checks."""
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product ID {data.product_id} not found",
        )

    sku_exists = db.query(ProductVariant).filter(ProductVariant.sku == data.sku).first()
    if sku_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product variant with SKU '{data.sku}' already exists",
        )

    variant = ProductVariant(
        product_id=data.product_id,
        sku=data.sku,
        name=data.name,
        price_delta=data.price_delta,
        is_active=data.is_active,
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant


def get_variant(db: Session, variant_id: int) -> ProductVariant:
    """Retrieve variant by ID or raise 404."""
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product variant ID {variant_id} not found",
        )
    return variant


def list_variants(db: Session, product_id: Optional[int] = None) -> List[ProductVariant]:
    """List variants, optionally filtered by product_id."""
    query = db.query(ProductVariant)
    if product_id is not None:
        query = query.filter(ProductVariant.product_id == product_id)
    return query.order_by(ProductVariant.id).all()


def compute_effective_price(product: Product, variant: Optional[ProductVariant] = None) -> Decimal:
    """Computes base product sales_price + variant price_delta."""
    base = product.sales_price or Decimal("0.00")
    delta = variant.price_delta if variant else Decimal("0.00")
    return base + delta
