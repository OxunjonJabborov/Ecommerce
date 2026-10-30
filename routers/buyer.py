from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends

from enums import Roles
from database import get_db
from models import User, Product, Order, OrderItem
from dependencies import get_current_user, role_checker
from schemas.ecommerce import OrderCreate, OrderOut, ProductOut


buyer_router = APIRouter(prefix="/api", tags=["Buyer"])


@buyer_router.get("/products", response_model=list[ProductOut])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Product))
    return result.all()


@buyer_router.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi...")
    return product


@buyer_router.post("/orders", response_model=OrderOut)
async def create_order(order_in: OrderCreate, current_user: User = Depends(role_checker(Roles.BUYER, Roles.ADMIN)), db: AsyncSession = Depends(get_db)):
    order = Order(buyer_id=current_user.id, total_price=0)
    db.add(order)
    await db.flush()

    total = 0.0
    for item_data in order_in.items:
        product = await db.scalar(select(Product).where(Product.id == item_data.product_id))
        if not product:
            raise HTTPException(status_code=404, detail=f"Mahsulot {item_data.product_id} topilmadi...")
        if product.stock < item_data.quantity:
            raise HTTPException(status_code=400, detail=f"{product.title} da mahsulotlar yetarli emas...")

        product.stock -= item_data.quantity
        total += product.price * item_data.quantity

        db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=item_data.quantity, unit_price=product.price))

    order.total_price = total
    await db.commit()
    await db.refresh(order)
    return order


@buyer_router.get("/orders/my", response_model=list[OrderOut])
async def my_orders(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Order).where(Order.buyer_id == current_user.id))
    return result.all()
