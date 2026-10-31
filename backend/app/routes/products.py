"""Products and Plans routes."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.product import ProductCreate, ProductRead, PlanCreate, PlanRead
from backend.app.schemas.common import StandardResponse, ok
from backend.app.services.product_service import (
    create_product, list_products, get_product, update_product,
    create_plan, list_plans, get_plan,
)
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.models.user import User

router = APIRouter(prefix="/products", tags=["Products & Plans"])
plans_router = APIRouter(prefix="/plans", tags=["Products & Plans"])


# ── Products ──────────────────────────────────────────────────────────────────

@router.get("", response_model=StandardResponse[list[ProductRead]])
def get_products(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return ok([ProductRead.model_validate(p) for p in list_products(db)])


@router.post("", response_model=StandardResponse[ProductRead], status_code=status.HTTP_201_CREATED)
def add_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    return ok(ProductRead.model_validate(create_product(payload, db)), "Product created.")


@router.get("/{product_id}", response_model=StandardResponse[ProductRead])
def read_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return ok(ProductRead.model_validate(get_product(product_id, db)))


@router.patch("/{product_id}", response_model=StandardResponse[ProductRead])
def patch_product(
    product_id: int,
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    return ok(ProductRead.model_validate(update_product(product_id, payload, db)), "Product updated.")


# ── Plans ─────────────────────────────────────────────────────────────────────

@plans_router.get("", response_model=StandardResponse[list[PlanRead]])
def get_plans(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return ok([PlanRead.model_validate(p) for p in list_plans(db)])


@plans_router.post("", response_model=StandardResponse[PlanRead], status_code=status.HTTP_201_CREATED)
def add_plan(
    payload: PlanCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    return ok(PlanRead.model_validate(create_plan(payload, db)), "Plan created.")


@plans_router.get("/{plan_id}", response_model=StandardResponse[PlanRead])
def read_plan(plan_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return ok(PlanRead.model_validate(get_plan(plan_id, db)))
