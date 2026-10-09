from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class StockTransaction(Base):
    __tablename__ = "stock_transactions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    type = Column(String, nullable=False)  # PURCHASE | SALE | ADJUSTMENT
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    note = Column(String)

    product = relationship("Product", back_populates="stock_transactions")
