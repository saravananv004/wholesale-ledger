from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth.deps import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.stock import StockTransaction
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut, StockAdjustment

router = APIRouter(prefix="/api/v1/products", tags=["products"])


@router.get("", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Product).filter(Product.business_id == user.business_id).all()


@router.post("", response_model=ProductOut)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = Product(**payload.model_dump(), business_id=user.business_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id, Product.business_id == user.business_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@router.post("/{product_id}/stock-transactions", response_model=ProductOut)
def adjust_stock(
    product_id: int,
    payload: StockAdjustment,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id, Product.business_id == user.business_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.stock_qty += payload.quantity
    if product.stock_qty < 0:
        raise HTTPException(status_code=400, detail="Stock cannot go negative")

    db.add(StockTransaction(
        product_id=product.id,
        type=payload.type,
        quantity=payload.quantity,
        note=payload.note,
    ))
    db.commit()
    db.refresh(product)
    return product
