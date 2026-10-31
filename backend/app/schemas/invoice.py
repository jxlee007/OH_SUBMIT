"""Invoice and InvoiceLine schemas."""
from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, field_validator


class GenerateInvoiceRequest(BaseModel):
    """Request to generate an invoice for a subscription."""
    subscription_id: int
    billing_period_key: str  # e.g. "2026-10", "2026-W44"
    due_date: Optional[date] = None
    discount_code: Optional[str] = None


class InvoiceLineRead(BaseModel):
    id: int
    description: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal
    discount_amount: Decimal
    net_amount: Decimal
    tax_amount: Decimal
    amount: Decimal
    model_config = {"from_attributes": True}


class InvoiceRead(BaseModel):
    id: int
    subscription_id: int
    customer_id: int
    billing_period_key: str
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    due_date: Optional[date]
    status: str
    notes: Optional[str]
    lines: List[InvoiceLineRead] = []
    model_config = {"from_attributes": True}


class InvoiceStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        allowed = ("draft", "confirmed", "paid")
        if v not in allowed:
            raise ValueError(f"must be one of: {', '.join(allowed)}")
        return v
