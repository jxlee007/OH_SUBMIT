"""Subscription service — creation and lifecycle transitions."""
import uuid
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.subscription import Subscription, SubscriptionLine, STATUS_TRANSITIONS
from backend.app.models.user import User
from backend.app.models.product import Plan
from backend.app.schemas.subscription import SubscriptionCreate, SubscriptionStatusUpdate


def _generate_number() -> str:
    return f"SUB-{uuid.uuid4().hex[:8].upper()}"


def _compute_line_amount(quantity: int, unit_price: Decimal) -> Decimal:
    return (Decimal(str(quantity)) * unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def create_subscription(payload: SubscriptionCreate, db: Session) -> Subscription:
    """Create a new subscription in Draft status."""
    # Validate foreign keys
    customer = db.query(User).filter(User.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Customer not found.")
    plan = db.query(Plan).filter(Plan.id == payload.plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Plan not found.")

    sub = Subscription(
        number=_generate_number(),
        customer_id=payload.customer_id,
        plan_id=payload.plan_id,
        start_date=payload.start_date,
        expiry_date=payload.expiry_date,
        payment_terms=payload.payment_terms,
        notes=payload.notes,
        status="draft",
    )
    db.add(sub)
    db.flush()  # get sub.id before adding lines

    for line_data in payload.lines:
        amount = _compute_line_amount(line_data.quantity, line_data.unit_price)
        line = SubscriptionLine(
            subscription_id=sub.id,
            product_id=line_data.product_id,
            description=line_data.description,
            quantity=line_data.quantity,
            unit_price=line_data.unit_price,
            tax_rate=line_data.tax_rate,
            amount=amount,
        )
        db.add(line)

    db.commit()
    db.refresh(sub)
    return sub


def list_subscriptions(db: Session, customer_id: int | None = None, status_filter: str | None = None) -> list[Subscription]:
    q = db.query(Subscription)
    if customer_id:
        q = q.filter(Subscription.customer_id == customer_id)
    if status_filter:
        q = q.filter(Subscription.status == status_filter)
    return q.all()


def get_subscription(sub_id: int, db: Session) -> Subscription:
    sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found.")
    return sub


def update_subscription_status(sub_id: int, payload: SubscriptionStatusUpdate, db: Session) -> Subscription:
    """Advance subscription status following allowed transitions."""
    sub = get_subscription(sub_id, db)
    allowed = STATUS_TRANSITIONS.get(sub.status, [])
    if payload.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{sub.status}' to '{payload.status}'. Allowed: {allowed}",
        )
    sub.status = payload.status
    db.commit()
    db.refresh(sub)
    return sub
