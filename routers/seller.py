import shutil
import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession as Session
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File

from enums import Roles
from database import get_db
from config import PRODUCT_FOLDER
from models import Users, Products
from dependencies import role_checker
from schemas.ecommerce import ProductCreate, ProductUpdate, ProductOut


seller_router = APIRouter(prefix="/api/seller", tags=["Seller"])


@seller_router.post("/products", response_model=ProductOut)
async def create_product(product_in: ProductCreate, current_user: Users = Depends(role_checker(Roles.ADMIN, Roles.SELLER)), db: Session = Depends(get_db)):
    product = Products(**product_in.model_dump(), seller_id=current_user.id)
    db.add(product)
    await db.commit()

    result = await db.scalar(select(Products).where(Products.id == product.id).options(selectinload(Products.tags)))
    return result


@seller_router.post("/products/{product_id}/image")
async def upload_product_image(product_id: int, file: UploadFile = File(...), current_user: Users = Depends(role_checker(Roles.SELLER, Roles.ADMIN)), db: Session = Depends(get_db)):
    product = await db.scalar(select(Products).where(Products.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi...")
    if current_user.id != product.seller_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Bu sizning mahsulotingiz emas...")

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
async def update_product(product_id: int, data: ProductUpdate, current_user: Users = Depends(role_checker(Roles.SELLER, Roles.ADMIN)), db: Session = Depends(get_db)):
    product = await db.scalar(select(Products).where(Products.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi...")
    if current_user.id != product.seller_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Bu sizning mahsulotingiz emas...")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(product, key, value)

    await db.commit()

    result = await db.scalar(select(Products).where(Products.id == product.id).options(selectinload(Products.tags)))
    return result


@seller_router.delete("/products/{product_id}")
async def delete_product(product_id: int, current_user: Users = Depends(role_checker(Roles.SELLER, Roles.ADMIN)), db: Session = Depends(get_db)):
    product = await db.scalar(select(Products).where(Products.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi...")
    if current_user.id != product.seller_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Bu siznig mahsulotingiz emas, uni o'chirolmaysiz...")

    await db.delete(product)
    await db.commit()
    return {"detail": "Mahsulot o'chirildi..."}
