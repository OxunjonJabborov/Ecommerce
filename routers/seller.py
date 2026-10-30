import shutil
import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File

from enums import Roles
from database import get_db
from config import PRODUCT_FOLDER
from models import User, Product
from dependencies import role_checker
from schemas.ecommerce import ProductCreate, ProductUpdate, ProductOut


seller_router = APIRouter(prefix="/api/seller", tags=["Seller"])


async def get_own_product(product_id: int, user: User, db: AsyncSession) -> Product:
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi...")
    if user.id != product.seller_id and user.role != Roles.ADMIN:
        raise HTTPException(status_code=403, detail="Bu sizning mahsulotingiz emas...")
    return product


@seller_router.post("/products", response_model=ProductOut)
async def create_product(product_in: ProductCreate, current_user: User = Depends(role_checker(Roles.ADMIN, Roles.SELLER)), db: AsyncSession = Depends(get_db)):
    product = Product(**product_in.model_dump(), seller_id=current_user.id)
    db.add(product)
    await db.commit()

    result = await db.scalar(select(Product).where(Product.id == product.id).options(selectinload(Product.tags)))
    return result


@seller_router.post("/products/{product_id}/image")
async def upload_product_image(product_id: int, file: UploadFile = File(...), current_user: User = Depends(role_checker(Roles.SELLER, Roles.ADMIN)), db: AsyncSession = Depends(get_db)):
    product = await get_own_product(product_id, current_user, db)

    file_extension = (file.filename or "").split(".", 1)[-1] if "." in (file.filename or "") else "bin"
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_location = f"{PRODUCT_FOLDER}/{filename}"
    static_location = f"/uploads/products/{filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    product.image_url = static_location
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return {"detail": "Mahsulot rasmi muvaffaqiyatli yuklandi...", "image_url": static_location}


@seller_router.put("/products/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, data: ProductUpdate, current_user: User = Depends(role_checker(Roles.SELLER, Roles.ADMIN)), db: AsyncSession = Depends(get_db)):
    product = await get_own_product(product_id, current_user, db)

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(product, key, value)

    await db.commit()

    result = await db.scalar(select(Product).where(Product.id == product.id).options(selectinload(Product.tags)))
    return result


@seller_router.delete("/products/{product_id}")
async def delete_product(product_id: int, current_user: User = Depends(role_checker(Roles.SELLER, Roles.ADMIN)), db: AsyncSession = Depends(get_db)):
    product = await get_own_product(product_id, current_user, db)

    await db.delete(product)
    await db.commit()
    return {"detail": "Mahsulot o'chirildi..."}
