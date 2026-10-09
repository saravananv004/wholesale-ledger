from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Retailer(Base):
    __tablename__ = "retailers"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    shop_name = Column(String, nullable=False)
    owner_name = Column(String)
    phone = Column(String)
    address = Column(String)
    opening_balance = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="retailers")
    orders = relationship("Order", back_populates="retailer")
    ledger_transactions = relationship("LedgerTransaction", back_populates="retailer")
