from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String)
    sku = Column(String)
    unit = Column(String)
    cost_price = Column(Numeric(10, 2), default=0)
    selling_price = Column(Numeric(10, 2), nullable=False)
    stock_qty = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, default=5)
    image_url = Column(String)
    active = Column(Boolean, default=True)

    business = relationship("Business", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    stock_transactions = relationship("StockTransaction", back_populates="product")
