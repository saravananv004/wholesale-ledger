from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class LedgerTransaction(Base):
    __tablename__ = "ledger_transactions"

    id = Column(Integer, primary_key=True, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    type = Column(String, nullable=False)  # DEBIT | CREDIT
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    note = Column(String)
    running_balance = Column(Numeric(10, 2), nullable=False)

    retailer = relationship("Retailer", back_populates="ledger_transactions")
    order = relationship("Order", back_populates="ledger_transaction")
