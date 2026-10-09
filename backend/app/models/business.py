from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)

    users = relationship("User", back_populates="business")
    products = relationship("Product", back_populates="business")
    retailers = relationship("Retailer", back_populates="business")
    orders = relationship("Order", back_populates="business")
    order_requests = relationship("OrderRequest", back_populates="business")
