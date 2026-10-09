from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.auth.deps import get_current_user
from app.models.user import User
from app.models.order import Order
from app.models.product import Product
from app.models.retailer import Retailer
from app.models.order_request import OrderRequest
from app.services.ledger_service import get_current_balance

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/today")
def dashboard_today(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    todays_sales = (
        db.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.business_id == user.business_id, Order.order_date >= today_start, Order.status == "CONFIRMED")
        .scalar()
    )

    low_stock = (
        db.query(Product)
        .filter(Product.business_id == user.business_id, Product.stock_qty <= Product.low_stock_threshold, Product.active == True)  # noqa: E712
        .all()
    )

    retailers = db.query(Retailer).filter(Retailer.business_id == user.business_id).all()
    balances = [(r, get_current_balance(db, r.id)) for r in retailers]
    total_due = sum(b for _, b in balances)
    top_debtors = sorted(balances, key=lambda x: x[1], reverse=True)[:5]

    pending_requests = (
        db.query(func.count(OrderRequest.id))
        .filter(OrderRequest.business_id == user.business_id, OrderRequest.status == "NEW")
        .scalar()
    )

    return {
        "todays_sales": float(todays_sales),
        "total_outstanding_dues": float(total_due),
        "low_stock_items": [{"id": p.id, "name": p.name, "stock_qty": p.stock_qty} for p in low_stock],
        "top_debtors": [
            {"retailer_id": r.id, "shop_name": r.shop_name, "balance": float(bal)} for r, bal in top_debtors
        ],
        "pending_order_requests": pending_requests,
    }
