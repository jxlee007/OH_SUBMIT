"""Quotation template schemas."""
from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class QuotationTemplateLineCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0)
    unit_price: Decimal = Field(..., gt=0)
    tax_rate: Decimal = Field(default=Decimal("18.00"), ge=0)


class QuotationTemplateLineRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal
    model_config = {"from_attributes": True}


class QuotationTemplateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: Optional[str] = None
    plan_id: Optional[int] = None
    validity_days: int = Field(default=30, gt=0)
    lines: List[QuotationTemplateLineCreate] = []


class QuotationTemplateRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    plan_id: Optional[int]
    validity_days: int
    lines: List[QuotationTemplateLineRead] = []
    model_config = {"from_attributes": True}


class InstantiateTemplateRequest(BaseModel):
    customer_id: int
    start_date: Optional[date] = None
    payment_terms: Optional[str] = "Net 30"
