"""Payment schemas."""
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, field_validator


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: Decimal
    method: str = "bank_transfer"
    payment_date: date
    reference: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class PaymentRead(PaymentCreate):
    id: int
    model_config = {"from_attributes": True}
