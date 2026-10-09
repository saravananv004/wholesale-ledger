from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OrderRequestItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderRequestCreate(BaseModel):
    shop_name: str
    contact_phone: str
    note: Optional[str] = None
    items: List[OrderRequestItemCreate]


class OrderRequestItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class OrderRequestOut(BaseModel):
    id: int
    business_id: int
    shop_name: str
    contact_phone: str
    note: Optional[str] = None
    status: str
    created_at: datetime
    items: List[OrderRequestItemOut] = []

    class Config:
        from_attributes = True


class PublicProductOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    selling_price: float
    image_url: Optional[str] = None
    in_stock: bool

    class Config:
        from_attributes = True
