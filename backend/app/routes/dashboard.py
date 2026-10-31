"""Dashboard summary route."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.dashboard import DashboardSummary
from backend.app.schemas.common import StandardResponse, ok
from backend.app.services.dashboard_service import get_summary
from backend.app.services.auth_service import require_roles
from backend.app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=StandardResponse[DashboardSummary])
def summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    return ok(get_summary(db))
