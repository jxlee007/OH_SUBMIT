"""Payment routes."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.core.database import get_db
from backend.app.schemas.payment import PaymentCreate, PaymentRead
from backend.app.schemas.common import StandardResponse, ok
from backend.app.services.payment_service import record_payment, list_payments, list_outstanding_invoices
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.models.user import User
from backend.app.schemas.invoice import InvoiceRead

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=StandardResponse[list[PaymentRead]])
def get_payments(
    invoice_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    return ok([PaymentRead.model_validate(p) for p in list_payments(db, invoice_id=invoice_id)])


@router.post("", response_model=StandardResponse[PaymentRead], status_code=status.HTTP_201_CREATED)
def add_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    return ok(PaymentRead.model_validate(record_payment(payload, db)), "Payment recorded.")


@router.get("/outstanding", response_model=StandardResponse[list[InvoiceRead]])
def get_outstanding(db: Session = Depends(get_db), _: User = Depends(require_roles("admin", "staff"))):
    return ok([InvoiceRead.model_validate(i) for i in list_outstanding_invoices(db)])
