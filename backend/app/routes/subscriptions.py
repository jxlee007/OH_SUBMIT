"""Subscription routes."""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.subscription import SubscriptionCreate, SubscriptionRead, SubscriptionStatusUpdate
from backend.app.schemas.common import StandardResponse, ok
from backend.app.services.subscription_service import (
    create_subscription, list_subscriptions, get_subscription, update_subscription_status,
    pause_subscription, resume_subscription,
)
from backend.app.services.scheduler_service import run_billing_cycle
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.models.user import User

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("", response_model=StandardResponse[list[SubscriptionRead]])
def get_subscriptions(
    customer_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Customers can only see their own subscriptions
    if current_user.role == "customer":
        customer_id = current_user.id
    subs = list_subscriptions(db, customer_id=customer_id, status_filter=status_filter)
    return ok([SubscriptionRead.model_validate(s) for s in subs])


@router.post("", response_model=StandardResponse[SubscriptionRead], status_code=status.HTTP_201_CREATED)
def add_subscription(
    payload: SubscriptionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    return ok(SubscriptionRead.model_validate(create_subscription(payload, db)), "Subscription created.")


@router.get("/{sub_id}", response_model=StandardResponse[SubscriptionRead])
def read_subscription(
    sub_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = get_subscription(sub_id, db)
    if current_user.role == "customer" and sub.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this subscription.",
        )
    return ok(SubscriptionRead.model_validate(sub))


@router.patch("/{sub_id}/status", response_model=StandardResponse[SubscriptionRead])
def change_subscription_status(
    sub_id: int,
    payload: SubscriptionStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    return ok(
        SubscriptionRead.model_validate(update_subscription_status(sub_id, payload, db)),
        "Status updated.",
    )


@router.post("/{sub_id}/pause", response_model=StandardResponse[SubscriptionRead])
def pause_sub(
    sub_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    """Pause an active subscription if plan permits."""
    return ok(
        SubscriptionRead.model_validate(pause_subscription(sub_id, db)),
        "Subscription paused.",
    )


@router.post("/{sub_id}/resume", response_model=StandardResponse[SubscriptionRead])
def resume_sub(
    sub_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    """Resume a paused subscription."""
    return ok(
        SubscriptionRead.model_validate(resume_subscription(sub_id, db)),
        "Subscription resumed to active.",
    )


@router.post("/billing-run", response_model=StandardResponse[dict])
def trigger_billing_run(
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    """Trigger manual billing and renewal evaluation cycle (Admin only)."""
    result = run_billing_cycle(db, target_date=target_date)
    return ok(result, "Billing cycle executed successfully.")
