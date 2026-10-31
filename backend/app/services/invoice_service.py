"""Invoice service — generate from subscription, no double-billing, status transitions."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.invoice import Invoice, InvoiceLine, INVOICE_STATUS_TRANSITIONS
from backend.app.models.subscription import Subscription
from backend.app.schemas.invoice import GenerateInvoiceRequest, InvoiceStatusUpdate


def _round2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def generate_invoice(payload: GenerateInvoiceRequest, db: Session) -> Invoice:
    """Generate an invoice for a subscription period. Returns 409 on double-billing."""
    sub = db.query(Subscription).filter(Subscription.id == payload.subscription_id).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found.")
    if sub.status not in ("confirmed", "active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoices can only be generated for confirmed or active subscriptions.",
        )

    # Double-billing guard (also enforced by DB UNIQUE constraint)
    existing = db.query(Invoice).filter(
        Invoice.subscription_id == sub.id,
        Invoice.billing_period_key == payload.billing_period_key,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invoice already exists for period '{payload.billing_period_key}'.",
        )

    # Build invoice lines from subscription lines
    subtotal = Decimal("0.00")
    total_tax = Decimal("0.00")
    invoice_lines = []

    for sub_line in sub.lines:
        net = _round2(Decimal(str(sub_line.quantity)) * sub_line.unit_price)
        tax = _round2(net * sub_line.tax_rate / Decimal("100"))
        gross = _round2(net + tax)
        subtotal += net
        total_tax += tax
        invoice_lines.append(InvoiceLine(
            product_id=sub_line.product_id,
            description=sub_line.description or (sub_line.product.name if sub_line.product else "Service"),
            quantity=sub_line.quantity,
            unit_price=sub_line.unit_price,
            tax_rate=sub_line.tax_rate,
            net_amount=net,
            tax_amount=tax,
            amount=gross,
        ))

    invoice = Invoice(
        subscription_id=sub.id,
        customer_id=sub.customer_id,
        billing_period_key=payload.billing_period_key,
        subtotal=_round2(subtotal),
        tax_amount=_round2(total_tax),
        total=_round2(subtotal + total_tax),
        due_date=payload.due_date,
        status="draft",
    )
    db.add(invoice)
    db.flush()

    for line in invoice_lines:
        line.invoice_id = invoice.id
        db.add(line)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invoice already exists for period '{payload.billing_period_key}'.",
        )

    db.refresh(invoice)
    return invoice


def list_invoices(
    db: Session,
    customer_id: int | None = None,
    status_filter: str | None = None,
    overdue_only: bool = False,
) -> list[Invoice]:
    q = db.query(Invoice)
    if customer_id:
        q = q.filter(Invoice.customer_id == customer_id)
    if status_filter:
        q = q.filter(Invoice.status == status_filter)
    if overdue_only:
        today = date.today()
        q = q.filter(Invoice.status != "paid", Invoice.due_date < today)
    return q.all()


def get_invoice(invoice_id: int, db: Session) -> Invoice:
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")
    return inv


def update_invoice_status(invoice_id: int, payload: InvoiceStatusUpdate, db: Session) -> Invoice:
    inv = get_invoice(invoice_id, db)
    allowed = INVOICE_STATUS_TRANSITIONS.get(inv.status, [])
    if payload.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{inv.status}' to '{payload.status}'. Allowed: {allowed}",
        )
    inv.status = payload.status
    db.commit()
    db.refresh(inv)
    return inv
