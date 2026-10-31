"""Product and Plan schemas."""
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, field_validator


class ProductCreate(BaseModel):
    name: str
    product_type: str = "service"
    sales_price: Decimal = Decimal("0.00")
    cost_price: Decimal = Decimal("0.00")
    notes: Optional[str] = None


class ProductRead(ProductCreate):
    id: int
    is_active: bool
    model_config = {"from_attributes": True}


class PlanCreate(BaseModel):
    product_id: int
    name: str
    price: Decimal
    billing_period: str = "monthly"
    min_quantity: int = 1
    available_from: Optional[date] = None
    available_until: Optional[date] = None
    auto_close: bool = False
    can_pause: bool = False
    can_renew: bool = True

    @field_validator("billing_period")
    @classmethod
    def billing_period_valid(cls, v: str) -> str:
        allowed = ("daily", "weekly", "monthly", "yearly")
        if v not in allowed:
            raise ValueError(f"must be one of: {', '.join(allowed)}")
        return v

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("price must be non-negative")
        return v


class PlanRead(PlanCreate):
    id: int
    is_active: bool
    model_config = {"from_attributes": True}
