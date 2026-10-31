"""Dashboard summary schemas."""
from decimal import Decimal
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    active_subscriptions: int
    total_revenue: Decimal
    outstanding_amount: Decimal
    overdue_invoices: int
    paid_invoices: int
    draft_invoices: int
    confirmed_invoices: int
