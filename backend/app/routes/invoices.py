"""Invoice routes."""
from fastapi import APIRouter, Depends, Query, status, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.core.database import get_db
from backend.app.schemas.invoice import GenerateInvoiceRequest, InvoiceRead, InvoiceStatusUpdate
from backend.app.schemas.common import StandardResponse, ok
from backend.app.services.invoice_service import (
    generate_invoice, list_invoices, get_invoice, update_invoice_status,
)
from backend.app.services.pdf_service import render_invoice_pdf
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.models.user import User

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("", response_model=StandardResponse[list[InvoiceRead]])
def get_invoices(
    customer_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    overdue_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "customer":
        customer_id = current_user.id
    invoices = list_invoices(db, customer_id=customer_id, status_filter=status_filter, overdue_only=overdue_only)
    return ok([InvoiceRead.model_validate(i) for i in invoices])


@router.post("", response_model=StandardResponse[InvoiceRead], status_code=status.HTTP_201_CREATED)
@router.post("/generate", response_model=StandardResponse[InvoiceRead], status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: GenerateInvoiceRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    return ok(InvoiceRead.model_validate(generate_invoice(payload, db)), "Invoice generated.")


@router.get("/{invoice_id}", response_model=StandardResponse[InvoiceRead])
def read_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = get_invoice(invoice_id, db)
    if current_user.role == "customer" and inv.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this invoice.",
        )
    return ok(InvoiceRead.model_validate(inv))


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download invoice rendered as pure PDF document.
    Admin & staff may download any invoice; customers may only download their own (403).
    """
    inv = get_invoice(invoice_id, db)
    if current_user.role == "customer" and inv.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this invoice.",
        )
    pdf_bytes = render_invoice_pdf(inv)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice-{inv.id}.pdf",
        },
    )


@router.patch("/{invoice_id}/status", response_model=StandardResponse[InvoiceRead])
def change_invoice_status(
    invoice_id: int,
    payload: InvoiceStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "staff")),
):
    return ok(
        InvoiceRead.model_validate(update_invoice_status(invoice_id, payload, db)),
        "Invoice status updated.",
    )
