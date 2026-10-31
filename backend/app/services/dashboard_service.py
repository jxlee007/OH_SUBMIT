"""Dashboard aggregation service."""
from datetime import date
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models.subscription import Subscription
from backend.app.models.invoice import Invoice
from backend.app.models.payment import Payment
from backend.app.schemas.dashboard import DashboardSummary


def get_summary(db: Session) -> DashboardSummary:
    """Aggregate KPIs for the summary dashboard."""
    active_subscriptions: int = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.status == "active")
        .scalar() or 0
    )

    total_revenue: Decimal = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .scalar()
    )

    outstanding_amount: Decimal = (
        db.query(func.coalesce(func.sum(Invoice.total), 0))
        .filter(Invoice.status == "confirmed")
        .scalar()
    )

    today = date.today()
    overdue_invoices: int = (
        db.query(func.count(Invoice.id))
        .filter(Invoice.status != "paid", Invoice.due_date < today)
        .scalar() or 0
    )

    paid_invoices: int = (
        db.query(func.count(Invoice.id)).filter(Invoice.status == "paid").scalar() or 0
    )
    draft_invoices: int = (
        db.query(func.count(Invoice.id)).filter(Invoice.status == "draft").scalar() or 0
    )
    confirmed_invoices: int = (
        db.query(func.count(Invoice.id)).filter(Invoice.status == "confirmed").scalar() or 0
    )

    return DashboardSummary(
        active_subscriptions=active_subscriptions,
        total_revenue=Decimal(str(total_revenue)),
        outstanding_amount=Decimal(str(outstanding_amount)),
        overdue_invoices=overdue_invoices,
        paid_invoices=paid_invoices,
        draft_invoices=draft_invoices,
        confirmed_invoices=confirmed_invoices,
    )
