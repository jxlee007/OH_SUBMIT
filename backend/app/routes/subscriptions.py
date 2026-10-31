"""Subscription routes."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.core.database import get_db
from backend.app.schemas.subscription import SubscriptionCreate, SubscriptionRead, SubscriptionStatusUpdate
from backend.app.schemas.common import StandardResponse, ok
from backend.app.services.subscription_service import (
    create_subscription, list_subscriptions, get_subscription, update_subscription_status,
)
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
def read_subscription(sub_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return ok(SubscriptionRead.model_validate(get_subscription(sub_id, db)))


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
