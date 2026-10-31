"""Plans router — endpoints for managing recurring subscription plans."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.plan import PlanCreate, PlanRead
from backend.app.schemas.common import StandardResponse, ok
from backend.app.services.plan_service import create_plan, list_plans, get_plan
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.models.user import User

router = APIRouter(prefix="/plans", tags=["Subscription Plans"])


@router.get("", response_model=StandardResponse[list[PlanRead]])
def get_plans(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Retrieve all available subscription plans (accessible to all authenticated roles)."""
    return ok([PlanRead.model_validate(p) for p in list_plans(db)])


@router.post("", response_model=StandardResponse[PlanRead], status_code=status.HTTP_201_CREATED)
def add_plan(
    payload: PlanCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    """Create a new subscription recurrence plan (admin & staff only)."""
    return ok(PlanRead.model_validate(create_plan(payload, db)), "Plan created successfully.")


@router.get("/{plan_id}", response_model=StandardResponse[PlanRead])
def read_plan(plan_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Retrieve single plan details."""
    return ok(PlanRead.model_validate(get_plan(plan_id, db)))
