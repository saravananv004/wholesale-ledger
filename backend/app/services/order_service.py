from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.stock import StockTransaction
from app.services.ledger_service import add_ledger_entry


class InsufficientStockError(Exception):
    pass


def create_order(
    db: Session,
    business_id: int,
    retailer_id: int,
    items: list[dict],  # [{product_id, quantity}]
    note: str | None = None,
) -> Order:
    """
    The single most important function in the system (Handbook Section 7).

    Inside ONE database transaction:
      1. Insert the order
      2. Insert order_items
      3. For each item: insert a stock_transactions row (SALE) and
         decrease products.stock_qty
      4. Insert one ledger_transactions row (DEBIT) for the order total

    If ANY step fails, everything rolls back -- stock is never left
    adjusted without a matching ledger entry, or vice versa.
    """
    try:
        order = Order(
            business_id=business_id,
            retailer_id=retailer_id,
            note=note,
            total_amount=Decimal("0"),
            status="CONFIRMED",
        )
        db.add(order)
        db.flush()  # get order.id

        total = Decimal("0")

        for item in items:
            product = (
                db.query(Product)
                .filter(Product.id == item["product_id"], Product.business_id == business_id)
                .with_for_update()
                .first()
            )
            if product is None:
                raise ValueError(f"Product {item['product_id']} not found")

            quantity = item["quantity"]
            if product.stock_qty < quantity:
                raise InsufficientStockError(
                    f"Not enough stock for '{product.name}': have {product.stock_qty}, need {quantity}"
                )

            unit_price = product.selling_price
            subtotal = unit_price * quantity
            total += subtotal

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )
            db.add(order_item)

            product.stock_qty -= quantity

            stock_txn = StockTransaction(
                product_id=product.id,
                type="SALE",
                quantity=-quantity,
                note=f"Order #{order.id}",
            )
            db.add(stock_txn)

        order.total_amount = total

        add_ledger_entry(
            db,
            retailer_id=retailer_id,
            entry_type="DEBIT",
            amount=total,
            note=f"Order #{order.id}",
            order_id=order.id,
        )

        db.commit()
        db.refresh(order)
        return order

    except Exception:
        db.rollback()
        raise


def cancel_order(db: Session, order_id: int, business_id: int) -> Order:
    """
    Reverses an order: restores stock and adds a matching CREDIT ledger
    entry so the retailer's balance goes back down. Atomic, same pattern
    as create_order.
    """
    try:
        order = (
            db.query(Order)
            .filter(Order.id == order_id, Order.business_id == business_id)
            .with_for_update()
            .first()
        )
        if order is None:
            raise ValueError("Order not found")
        if order.status == "CANCELLED":
            raise ValueError("Order already cancelled")

        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
            if product:
                product.stock_qty += item.quantity
                db.add(StockTransaction(
                    product_id=product.id,
                    type="ADJUSTMENT",
                    quantity=item.quantity,
                    note=f"Cancelled order #{order.id}",
                ))

        add_ledger_entry(
            db,
            retailer_id=order.retailer_id,
            entry_type="CREDIT",
            amount=order.total_amount,
            note=f"Reversal for cancelled order #{order.id}",
            order_id=order.id,
        )

        order.status = "CANCELLED"

        db.commit()
        db.refresh(order)
        return order

    except Exception:
        db.rollback()
        raise
