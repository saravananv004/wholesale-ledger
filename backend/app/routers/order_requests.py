from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.auth.deps import get_current_user
from app.models.user import User
from app.models.order_request import OrderRequest
from app.models.retailer import Retailer
from app.schemas.order_request import OrderRequestOut
from app.services.order_service import create_order, InsufficientStockError

router = APIRouter(prefix="/api/v1/order-requests", tags=["order-requests"])


@router.get("", response_model=List[OrderRequestOut])
def list_requests(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(OrderRequest).filter(OrderRequest.business_id == user.business_id)
    if status:
        query = query.filter(OrderRequest.status == status)
    return query.order_by(OrderRequest.created_at.desc()).all()


@router.patch("/{request_id}/confirm", response_model=OrderRequestOut)
def confirm_request(request_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Matches the request to an existing retailer (by phone) or creates a new
    one, then creates a REAL order using the exact same order_service logic
    as Section 7 -- no duplicated transaction logic.
    """
    req = (
        db.query(OrderRequest)
        .filter(OrderRequest.id == request_id, OrderRequest.business_id == user.business_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Order request not found")
    if req.status != "NEW" and req.status != "CONTACTED":
        raise HTTPException(status_code=400, detail=f"Request already {req.status}")

    retailer = (
        db.query(Retailer)
        .filter(Retailer.business_id == user.business_id, Retailer.phone == req.contact_phone)
        .first()
    )
    if not retailer:
        retailer = Retailer(
            business_id=user.business_id,
            shop_name=req.shop_name,
            phone=req.contact_phone,
            opening_balance=0,
        )
        db.add(retailer)
        db.flush()

    try:
        create_order(
            db,
            business_id=user.business_id,
            retailer_id=retailer.id,
            items=[{"product_id": i.product_id, "quantity": i.quantity} for i in req.items],
            note=f"From order request #{req.id}",
        )
    except InsufficientStockError as e:
        raise HTTPException(status_code=400, detail=str(e))

    req.status = "CONFIRMED"
    db.commit()
    db.refresh(req)
    return req


@router.patch("/{request_id}/reject", response_model=OrderRequestOut)
def reject_request(request_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    req = (
        db.query(OrderRequest)
        .filter(OrderRequest.id == request_id, OrderRequest.business_id == user.business_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Order request not found")
    req.status = "REJECTED"
    db.commit()
    db.refresh(req)
    return req
