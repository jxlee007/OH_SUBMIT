"""Subscription and SubscriptionLine schemas."""
from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, field_validator


class SubscriptionLineCreate(BaseModel):
    product_id: int
    description: Optional[str] = None
    quantity: int = 1
    unit_price: Decimal
    tax_rate: Decimal = Decimal("0.00")


class SubscriptionLineRead(SubscriptionLineCreate):
    id: int
    amount: Decimal
    model_config = {"from_attributes": True}


class SubscriptionCreate(BaseModel):
    customer_id: int
    plan_id: int
    start_date: date
    expiry_date: Optional[date] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    lines: List[SubscriptionLineCreate] = []


class SubscriptionRead(BaseModel):
    id: int
    number: str
    customer_id: int
    plan_id: int
    start_date: date
    expiry_date: Optional[date]
    payment_terms: Optional[str]
    status: str
    notes: Optional[str]
    lines: List[SubscriptionLineRead] = []
    model_config = {"from_attributes": True}


class SubscriptionStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        allowed = ("draft", "confirmed", "active", "closed")
        if v not in allowed:
            raise ValueError(f"must be one of: {', '.join(allowed)}")
        return v
