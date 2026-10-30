from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends

from enums import Roles
from database import get_db
from models import User
from dependencies import role_checker
from schemas.users import UserOut


admin_router = APIRouter(prefix="/api/admins", tags=["Admin"])


@admin_router.get("/users", response_model=list[UserOut])
async def get_all_users(db: AsyncSession = Depends(get_db), _user: User = Depends(role_checker((Roles.ADMIN)))):
    result = await db.scalars(select(User))
    return result.all()


@admin_router.put("/users/{user_id}/role", response_model=UserOut)
async def update_role(user_id: int, new_role: Roles, db: AsyncSession = Depends(get_db), _user: User = Depends(role_checker(Roles.ADMIN))):
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail='Foydalanuvchi topilmadi...')

    user.role = new_role.value
    await db.commit()
    await db.refresh(user)
    return user


@admin_router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(role_checker(Roles.ADMIN))):
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="foydalanuvchi topilmadi...")

    await db.delete(user)
    await db. commit()
    return {"detail": f"{user.email} o'chirildi..."}
