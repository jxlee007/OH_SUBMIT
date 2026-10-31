"""Discount rule business logic and concurrency-safe rule locking."""
from datetime import date
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.discount import DiscountRule
from backend.app.schemas.discount import DiscountRuleCreate, DiscountRuleUpdate


def list_discount_rules(db: Session) -> list[DiscountRule]:
    return db.query(DiscountRule).order_by(DiscountRule.created_at.desc()).all()


def get_discount_rule_by_id(rule_id: int, db: Session) -> DiscountRule:
    rule = db.query(DiscountRule).filter(DiscountRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Discount rule with ID {rule_id} not found.",
        )
    return rule


def create_discount_rule(payload: DiscountRuleCreate, db: Session) -> DiscountRule:
    existing = db.query(DiscountRule).filter(DiscountRule.code == payload.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Discount code '{payload.code}' already exists.",
        )

    rule = DiscountRule(
        code=payload.code,
        name=payload.name,
        rule_type=payload.rule_type,
        discount_value=payload.discount_value,
        applies_to=payload.applies_to,
        product_id=payload.product_id,
        min_amount=payload.min_amount,
        min_quantity=payload.min_quantity,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        usage_limit=payload.usage_limit,
        is_active=payload.is_active,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_discount_rule(rule_id: int, payload: DiscountRuleUpdate, db: Session) -> DiscountRule:
    rule = get_discount_rule_by_id(rule_id, db)
    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(rule, field, val)
    db.commit()
    db.refresh(rule)
    return rule


def delete_discount_rule(rule_id: int, db: Session) -> None:
    rule = get_discount_rule_by_id(rule_id, db)
    db.delete(rule)
    db.commit()


def get_and_lock_discount_rule(code: str, db: Session) -> DiscountRule:
    """Locks discount rule row within transaction via SELECT ... FOR UPDATE.
    Guarantees concurrency safety against concurrent invoices exceeding usage limit."""
    code_upper = code.strip().upper()
    # In SQLite (used in test), with_for_update is silently ignored or supported; in PostgreSQL it locks the row.
    rule = db.query(DiscountRule).filter(DiscountRule.code == code_upper).with_for_update().first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Discount code '{code_upper}' not found.",
        )
    if not rule.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Discount code '{code_upper}' is currently deactivated.",
        )

    today = date.today()
    if today < rule.valid_from or today > rule.valid_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Discount rule '{code_upper}' has expired or is not yet active (valid {rule.valid_from} to {rule.valid_to}).",
        )

    if rule.usage_limit is not None and rule.times_used >= rule.usage_limit:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Discount rule '{code_upper}' usage limit of {rule.usage_limit} has been exhausted.",
        )

    return rule
