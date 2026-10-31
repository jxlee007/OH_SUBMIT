"""Discount rule schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator, field_validator


class DiscountRuleCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Unique discount code")
    name: str = Field(..., min_length=2, max_length=120)
    rule_type: Literal["fixed", "percent"] = "percent"
    discount_value: Decimal = Field(..., gt=0)
    applies_to: Literal["subscription", "product"] = "subscription"
    product_id: Optional[int] = None
    min_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    min_quantity: int = Field(default=0, ge=0)
    valid_from: date
    valid_to: date
    usage_limit: Optional[int] = Field(default=None, ge=1)
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        return v.strip().upper()

    @model_validator(mode="after")
    def validate_rules(self) -> "DiscountRuleCreate":
        if self.rule_type == "percent" and self.discount_value > Decimal("100.00"):
            raise ValueError("Percentage discount cannot exceed 100%.")
        if self.valid_to < self.valid_from:
            raise ValueError("valid_to date cannot be earlier than valid_from date.")
        if self.applies_to == "product" and not self.product_id:
            raise ValueError("product_id is required when applies_to is 'product'.")
        return self


class DiscountRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    discount_value: Optional[Decimal] = Field(None, gt=0)
    min_amount: Optional[Decimal] = Field(None, ge=0)
    min_quantity: Optional[int] = Field(None, ge=0)
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    usage_limit: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class DiscountRuleOut(BaseModel):
    id: int
    code: str
    name: str
    rule_type: str
    discount_value: Decimal
    applies_to: str
    product_id: Optional[int]
    min_amount: Decimal
    min_quantity: int
    valid_from: date
    valid_to: date
    usage_limit: Optional[int]
    times_used: int
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
