from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    retailer_id: int
    items: List[OrderItemCreate]
    note: Optional[str] = None


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    business_id: int
    retailer_id: int
    order_date: datetime
    total_amount: Decimal
    status: str
    note: Optional[str] = None
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True
