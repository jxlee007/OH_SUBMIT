"""Products router — catalog management endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.product import ProductCreate, ProductRead
from backend.app.schemas.common import StandardResponse, ok
from backend.app.services.product_service import (
    create_product, list_products, get_product, update_product,
)
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=StandardResponse[list[ProductRead]])
def get_products(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Retrieve all catalog products."""
    return ok([ProductRead.model_validate(p) for p in list_products(db)])


@router.post("", response_model=StandardResponse[ProductRead], status_code=status.HTTP_201_CREATED)
def add_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    """Create a new catalog product (admin & staff only)."""
    return ok(ProductRead.model_validate(create_product(payload, db)), "Product created.")


@router.get("/{product_id}", response_model=StandardResponse[ProductRead])
def read_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Retrieve single product by ID."""
    return ok(ProductRead.model_validate(get_product(product_id, db)))


@router.patch("/{product_id}", response_model=StandardResponse[ProductRead])
def patch_product(
    product_id: int,
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    """Update a product (admin & staff only)."""
    return ok(ProductRead.model_validate(update_product(product_id, payload, db)), "Product updated.")
