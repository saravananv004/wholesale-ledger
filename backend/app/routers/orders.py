from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.deps import get_current_user
from app.models.user import User
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderOut
from app.services.order_service import create_order, cancel_order, InsufficientStockError

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("", response_model=OrderOut)
def new_order(payload: OrderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        order = create_order(
            db,
            business_id=user.business_id,
            retailer_id=payload.retailer_id,
            items=[item.model_dump() for item in payload.items],
            note=payload.note,
        )
        return order
    except InsufficientStockError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.business_id == user.business_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}/cancel", response_model=OrderOut)
def cancel(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return cancel_order(db, order_id=order_id, business_id=user.business_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
