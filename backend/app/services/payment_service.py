"""Payment service — record payment against invoice."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.payment import Payment
from backend.app.models.invoice import Invoice
from backend.app.schemas.payment import PaymentCreate


def record_payment(payload: PaymentCreate, db: Session) -> Payment:
    """Record a payment against a confirmed invoice."""
    invoice = db.query(Invoice).filter(Invoice.id == payload.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")
    if invoice.status not in ("confirmed", "paid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payments can only be recorded against confirmed invoices.",
        )
    payment = Payment(
        invoice_id=payload.invoice_id,
        amount=payload.amount,
        method=payload.method,
        payment_date=payload.payment_date,
        reference=payload.reference,
        notes=payload.notes,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def list_payments(db: Session, invoice_id: int | None = None) -> list[Payment]:
    q = db.query(Payment)
    if invoice_id:
        q = q.filter(Payment.invoice_id == invoice_id)
    return q.all()


def list_outstanding_invoices(db: Session) -> list[Invoice]:
    """Return all confirmed (unpaid) invoices."""
    return db.query(Invoice).filter(Invoice.status == "confirmed").all()
