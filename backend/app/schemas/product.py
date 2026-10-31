"""Product schemas — payload validation for base products."""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
# Re-export Plan schemas from dedicated plan module
from backend.app.schemas.plan import PlanCreate, PlanRead  # noqa: F401


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
