"""Discount rules routes — Admin CRUD and rule listing."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.auth_service import require_roles
from backend.app.models.user import User
from backend.app.schemas.common import StandardResponse, ok
from backend.app.schemas.discount import DiscountRuleCreate, DiscountRuleUpdate, DiscountRuleOut
from backend.app.services.discount_service import (
    list_discount_rules,
    get_discount_rule_by_id,
    create_discount_rule,
    update_discount_rule,
    delete_discount_rule,
)

router = APIRouter(prefix="/discounts", tags=["Discounts"])


@router.get("", response_model=StandardResponse[list[DiscountRuleOut]])
def list_discounts(
    current_user: User = Depends(require_roles("admin", "staff")),
    db: Session = Depends(get_db),
):
    rules = list_discount_rules(db)
    return ok([DiscountRuleOut.model_validate(r) for r in rules])


@router.get("/{rule_id}", response_model=StandardResponse[DiscountRuleOut])
def get_discount(
    rule_id: int,
    current_user: User = Depends(require_roles("admin", "staff")),
    db: Session = Depends(get_db),
):
    rule = get_discount_rule_by_id(rule_id, db)
    return ok(DiscountRuleOut.model_validate(rule))


@router.post("", response_model=StandardResponse[DiscountRuleOut], status_code=status.HTTP_201_CREATED)
def create_discount(
    payload: DiscountRuleCreate,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    rule = create_discount_rule(payload, db)
    return ok(DiscountRuleOut.model_validate(rule), "Discount rule created successfully.")


@router.patch("/{rule_id}", response_model=StandardResponse[DiscountRuleOut])
def update_discount(
    rule_id: int,
    payload: DiscountRuleUpdate,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    rule = update_discount_rule(rule_id, payload, db)
    return ok(DiscountRuleOut.model_validate(rule), "Discount rule updated successfully.")


@router.delete("/{rule_id}", response_model=StandardResponse[dict])
def delete_discount(
    rule_id: int,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    delete_discount_rule(rule_id, db)
    return ok({"deleted": True}, "Discount rule deleted successfully.")
