from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class ProductBase(BaseModel):
    name: str
    category: Optional[str] = None
    sku: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Decimal = Decimal("0")
    selling_price: Decimal
    stock_qty: int = 0
    low_stock_threshold: int = 5
    image_url: Optional[str] = None
    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    low_stock_threshold: Optional[int] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None


class ProductOut(ProductBase):
    id: int
    business_id: int

    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    type: str  # PURCHASE | ADJUSTMENT
    quantity: int  # positive to add, negative to subtract (for ADJUSTMENT)
    note: Optional[str] = None
