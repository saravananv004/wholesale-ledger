from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.ledger import LedgerTransaction
from app.models.retailer import Retailer


def get_current_balance(db: Session, retailer_id: int) -> Decimal:
    """
    Current balance = opening_balance + sum(DEBIT) - sum(CREDIT).
    We use the running_balance on the most recent ledger row when one exists,
    since it is already correct; otherwise we fall back to opening_balance.
    """
    retailer = db.query(Retailer).filter(Retailer.id == retailer_id).first()
    if retailer is None:
        raise ValueError("Retailer not found")

    last_entry = (
        db.query(LedgerTransaction)
        .filter(LedgerTransaction.retailer_id == retailer_id)
        .order_by(desc(LedgerTransaction.id))
        .first()
    )
    if last_entry:
        return last_entry.running_balance
    return retailer.opening_balance


def add_ledger_entry(
    db: Session,
    retailer_id: int,
    entry_type: str,  # "DEBIT" or "CREDIT"
    amount: Decimal,
    note: str | None = None,
    order_id: int | None = None,
) -> LedgerTransaction:
    """
    Adds one ledger row and updates running_balance.
    IMPORTANT: caller is responsible for committing the transaction as part of
    a larger atomic block (see order_service.create_order) so that this
    entry never gets saved without its matching stock/order changes.
    """
    current_balance = get_current_balance(db, retailer_id)

    if entry_type == "DEBIT":
        new_balance = current_balance + amount
    elif entry_type == "CREDIT":
        new_balance = current_balance - amount
    else:
        raise ValueError("entry_type must be DEBIT or CREDIT")

    entry = LedgerTransaction(
        retailer_id=retailer_id,
        order_id=order_id,
        type=entry_type,
        amount=amount,
        note=note,
        running_balance=new_balance,
    )
    db.add(entry)
    db.flush()  # get entry.id without committing yet
    return entry
