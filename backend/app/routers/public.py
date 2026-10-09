from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.product import Product
from app.models.business import Business
from app.models.order_request import OrderRequest, OrderRequestItem
from app.schemas.order_request import PublicProductOut, OrderRequestCreate, OrderRequestOut

router = APIRouter(prefix="/api/v1/public", tags=["public"])


@router.get("/catalog", response_model=List[PublicProductOut])
def get_catalog(business_id: int, db: Session = Depends(get_db)):
    """
    No-login product listing. business_id comes from the shared catalog
    link, e.g. https://yourapp.com/catalog?business=1
    """
    products = (
        db.query(Product)
        .filter(Product.business_id == business_id, Product.active == True)  # noqa: E712
        .all()
    )
    return [
        PublicProductOut(
            id=p.id,
            name=p.name,
            category=p.category,
            unit=p.unit,
            selling_price=float(p.selling_price),
            image_url=p.image_url,
            in_stock=p.stock_qty > 0,
        )
        for p in products
    ]


@router.post("/order-requests", response_model=OrderRequestOut)
def submit_order_request(business_id: int, payload: OrderRequestCreate, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    req = OrderRequest(
        business_id=business_id,
        shop_name=payload.shop_name,
        contact_phone=payload.contact_phone,
        note=payload.note,
        status="NEW",
    )
    db.add(req)
    db.flush()

    for item in payload.items:
        db.add(OrderRequestItem(request_id=req.id, product_id=item.product_id, quantity=item.quantity))

    db.commit()
    db.refresh(req)

    # Email notification hook -- see app/services/email_service.py
    from app.services.email_service import notify_new_order_request
    notify_new_order_request(req)

    return req
