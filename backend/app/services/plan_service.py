"""Plan service — isolated business logic for subscription recurrence plans."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.plan import Plan
from backend.app.models.product import Product
from backend.app.schemas.plan import PlanCreate


def create_plan(payload: PlanCreate, db: Session) -> Plan:
    """Create a new subscription plan linked to a product."""
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Linked product not found.")
    plan = Plan(**payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def list_plans(db: Session, active_only: bool = True) -> list[Plan]:
    """Retrieve all active subscription plans."""
    q = db.query(Plan)
    if active_only:
        q = q.filter(Plan.is_active == True)  # noqa: E712
    return q.all()


def get_plan(plan_id: int, db: Session) -> Plan:
    """Retrieve a plan by primary key."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found.")
    return plan
