"""Routes for managing product variants and attributes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.variant import (
    ProductAttributeCreate,
    ProductAttributeResponse,
    ProductVariantCreate,
    ProductVariantResponse,
)
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.services import variant_service

router = APIRouter(prefix="/api/products", tags=["Product Variants & Attributes"])


@router.post(
    "/attributes",
    response_model=ProductAttributeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product attribute (Admin only)",
)
def create_product_attribute(
    payload: ProductAttributeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    """Admin endpoint to create a product attribute (e.g., Hosting Region)."""
    return variant_service.create_attribute(db, payload)


@router.get(
    "/attributes",
    response_model=List[ProductAttributeResponse],
    summary="List product attributes",
)
def list_product_attributes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all available product attributes."""
    return variant_service.list_attributes(db)


@router.post(
    "/variants",
    response_model=ProductVariantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product variant (Admin only)",
)
def create_product_variant(
    payload: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    """Admin endpoint to create a product variant with SKU uniqueness and price delta."""
    variant = variant_service.create_variant(db, payload)
    eff_price = variant_service.compute_effective_price(variant.product, variant)
    return ProductVariantResponse(
        id=variant.id,
        product_id=variant.product_id,
        sku=variant.sku,
        name=variant.name,
        price_delta=variant.price_delta,
        is_active=variant.is_active,
        effective_price=eff_price,
    )


@router.get(
    "/variants",
    response_model=List[ProductVariantResponse],
    summary="List all product variants",
)
def list_all_variants(
    product_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List product variants, optionally filtered by product_id."""
    variants = variant_service.list_variants(db, product_id=product_id)
    results = []
    for v in variants:
        eff_price = variant_service.compute_effective_price(v.product, v)
        results.append(
            ProductVariantResponse(
                id=v.id,
                product_id=v.product_id,
                sku=v.sku,
                name=v.name,
                price_delta=v.price_delta,
                is_active=v.is_active,
                effective_price=eff_price,
            )
        )
    return results


@router.get(
    "/{product_id}/variants",
    response_model=List[ProductVariantResponse],
    summary="List variants for a specific product",
)
def list_product_specific_variants(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List variants for a given product ID."""
    return list_all_variants(product_id=product_id, db=db, current_user=current_user)
