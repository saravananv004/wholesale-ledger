from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth.deps import get_current_user
from app.models.user import User
from app.models.retailer import Retailer
from app.models.order import Order
from app.models.ledger import LedgerTransaction
from app.schemas.retailer import (
    RetailerCreate, RetailerUpdate, RetailerOut, PaymentCreate, LedgerEntryOut
)
from app.services.ledger_service import add_ledger_entry, get_current_balance

router = APIRouter(prefix="/api/v1/retailers", tags=["retailers"])


@router.get("", response_model=List[RetailerOut])
def list_retailers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    retailers = db.query(Retailer).filter(Retailer.business_id == user.business_id).all()
    result = []
    for r in retailers:
        out = RetailerOut.model_validate(r)
        out.current_balance = get_current_balance(db, r.id)
        result.append(out)
    return result


@router.post("", response_model=RetailerOut)
def create_retailer(payload: RetailerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    retailer = Retailer(**payload.model_dump(), business_id=user.business_id)
    db.add(retailer)
    db.commit()
    db.refresh(retailer)
    out = RetailerOut.model_validate(retailer)
    out.current_balance = retailer.opening_balance
    return out


@router.get("/{retailer_id}", response_model=RetailerOut)
def get_retailer(retailer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    retailer = db.query(Retailer).filter(Retailer.id == retailer_id, Retailer.business_id == user.business_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")
    out = RetailerOut.model_validate(retailer)
    out.current_balance = get_current_balance(db, retailer.id)
    return out


@router.patch("/{retailer_id}", response_model=RetailerOut)
def update_retailer(
    retailer_id: int,
    payload: RetailerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    retailer = db.query(Retailer).filter(Retailer.id == retailer_id, Retailer.business_id == user.business_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(retailer, key, value)
    db.commit()
    db.refresh(retailer)
    out = RetailerOut.model_validate(retailer)
    out.current_balance = get_current_balance(db, retailer.id)
    return out


@router.get("/{retailer_id}/ledger", response_model=List[LedgerEntryOut])
def get_ledger(retailer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    retailer = db.query(Retailer).filter(Retailer.id == retailer_id, Retailer.business_id == user.business_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")
    return (
        db.query(LedgerTransaction)
        .filter(LedgerTransaction.retailer_id == retailer_id)
        .order_by(LedgerTransaction.id)
        .all()
    )


@router.post("/{retailer_id}/payments", response_model=LedgerEntryOut)
def record_payment(
    retailer_id: int,
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    retailer = db.query(Retailer).filter(Retailer.id == retailer_id, Retailer.business_id == user.business_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")

    entry = add_ledger_entry(
        db, retailer_id=retailer_id, entry_type="CREDIT", amount=payload.amount, note=payload.note
    )
    db.commit()
    db.refresh(entry)
    return entry
@router.patch("/{retailer_id}", response_model=RetailerOut)
def update_retailer(
    retailer_id: int,
    payload: RetailerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    retailer = db.query(Retailer).filter(Retailer.id == retailer_id, Retailer.business_id == user.business_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")

    data = payload.model_dump(exclude_unset=True)

    if "shop_name" in data and not (data["shop_name"] or "").strip():
        raise HTTPException(status_code=400, detail="Shop name cannot be empty")

    if "opening_balance" in data:
        new_balance = data["opening_balance"]
        if new_balance is None:
            data.pop("opening_balance")
        elif new_balance != retailer.opening_balance:
            has_ledger = db.query(LedgerTransaction).filter(LedgerTransaction.retailer_id == retailer_id).count()
            if has_ledger:
                raise HTTPException(
                    status_code=400,
                    detail="Opening balance can't be changed after orders or payments exist. Record a payment instead.",
                )

    for key, value in data.items():
        setattr(retailer, key, value)
    db.commit()
    db.refresh(retailer)
    out = RetailerOut.model_validate(retailer)
    out.current_balance = get_current_balance(db, retailer.id)
    return out


@router.delete("/{retailer_id}", status_code=204)
def delete_retailer(retailer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    retailer = db.query(Retailer).filter(Retailer.id == retailer_id, Retailer.business_id == user.business_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")

    has_orders = db.query(Order).filter(Order.retailer_id == retailer_id).count()
    has_ledger = db.query(LedgerTransaction).filter(LedgerTransaction.retailer_id == retailer_id).count()
    if has_orders or has_ledger:
        raise HTTPException(
            status_code=400,
            detail="This retailer has orders or ledger history and can't be deleted. Edit it instead.",
        )

    db.delete(retailer)
    db.commit()
    return Response(status_code=204)