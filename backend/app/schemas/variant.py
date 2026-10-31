"""Pydantic schemas for product attributes and variants."""
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class ProductAttributeValueCreate(BaseModel):
    value: str = Field(..., min_length=1, max_length=60)


class ProductAttributeValueResponse(BaseModel):
    id: int
    attribute_id: int
    value: str
    model_config = {"from_attributes": True}


class ProductAttributeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)
    values: List[str] = []


class ProductAttributeResponse(BaseModel):
    id: int
    name: str
    values: List[ProductAttributeValueResponse] = []
    model_config = {"from_attributes": True}


class ProductVariantCreate(BaseModel):
    product_id: int
    sku: str = Field(..., min_length=1, max_length=60)
    name: str = Field(..., min_length=1, max_length=100)
    price_delta: Decimal = Field(default=Decimal("0.00"))
    is_active: bool = True


class ProductVariantResponse(BaseModel):
    id: int
    product_id: int
    sku: str
    name: str
    price_delta: Decimal
    is_active: bool
    effective_price: Optional[Decimal] = None
    model_config = {"from_attributes": True}
