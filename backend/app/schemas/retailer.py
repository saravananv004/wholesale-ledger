from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class RetailerBase(BaseModel):
    shop_name: str
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    opening_balance: Decimal = Decimal("0")


class RetailerCreate(RetailerBase):
    pass


class RetailerUpdate(BaseModel):
    shop_name: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    opening_balance: Optional[Decimal] = None


class RetailerOut(RetailerBase):
    id: int
    business_id: int
    created_at: datetime
    current_balance: Optional[Decimal] = None

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    amount: Decimal
    note: Optional[str] = None


class LedgerEntryOut(BaseModel):
    id: int
    type: str
    amount: Decimal
    date: datetime
    note: Optional[str] = None
    running_balance: Decimal
    order_id: Optional[int] = None

    class Config:
        from_attributes = True
