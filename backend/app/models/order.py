from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String, nullable=False, default="CONFIRMED")  # CONFIRMED | CANCELLED
    note = Column(String)

    business = relationship("Business", back_populates="orders")
    retailer = relationship("Retailer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    ledger_transaction = relationship("LedgerTransaction", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
