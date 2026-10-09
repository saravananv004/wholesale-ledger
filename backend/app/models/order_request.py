from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class OrderRequest(Base):
    __tablename__ = "order_requests"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    shop_name = Column(String, nullable=False)
    contact_phone = Column(String, nullable=False)
    note = Column(String)
    status = Column(String, nullable=False, default="NEW")  # NEW | CONTACTED | CONFIRMED | REJECTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="order_requests")
    items = relationship("OrderRequestItem", back_populates="request", cascade="all, delete-orphan")


class OrderRequestItem(Base):
    __tablename__ = "order_request_items"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("order_requests.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    request = relationship("OrderRequest", back_populates="items")
    product = relationship("Product")
