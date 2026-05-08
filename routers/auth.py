import os
import shutil
import security

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession as Session
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm

from enums import Roles
from database import get_db
from config import AVATAR_FOLDER
from models import Users, Profiles
from dependencies import get_current_user
from schemas.users import UserCreate, UserOut, ProfileUpdate, Token


auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])


@auth_router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = await db.scalar(select(Users).where(Users.email == user_in.email))
    if existing:
        raise HTTPException(status_code=400, detail="Bu email band...")

    user_dict = user_in.model_dump()
    admin_secret = user_dict.pop("admin_secret", None)
    hashed_password = security.get_password_hash(user_dict.pop("password"))
    user_dict.pop("role")

    count = await db.scalar(select(func.count()).select_from(Users))
    if count == 0:
        role = Roles.ADMIN.value
    elif admin_secret and admin_secret == os.getenv("ADMIN_SECRET_KEY"):
        role = Roles.ADMIN.value
    else:
        role = user_in.role.value

    user = Users(**user_dict, hashed_password=hashed_password, role=role)
    db.add(user)
    await db.flush()

    profile = Profiles(user_id=user.id)
    db.add(profile)
    await db.commit()

    user_id = user.id

    result = await db.scalar(select(Users).where(Users.id == user.id).options(selectinload(Users.profile)))
    return result


@auth_router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await db.scalar(select(Users).where(Users.email == form.username))
    if not user:
        raise HTTPException(status_code=400, detail="Email yoki parol noto'g'ri...")
    if not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Email yoki parol noto'g'ri...")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserOut)
async def get_me(current_user: Users = Depends(get_current_user)):
    return current_user


@auth_router.put("/me/profile", response_model=UserOut)
async def update_profile(data: ProfileUpdate, current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = await db.scalar(select(Profiles).where(Profiles.user_id == current_user.id))
    if not profile:
        profile = Profiles(user_id=current_user.id)
        db.add(profile)

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(current_user)
    return current_user


@auth_router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    file_extension = (file.filename or "").rsplit(".", 1)[-1] if "." in (file.filename or "") else "bin"
    file_location = f"{AVATAR_FOLDER}/{current_user.id}_avatar.{file_extension}"
    static_location = f"/uploads/avatars/{current_user.id}_avatar.{file_extension}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    profile = await db.scalar(select(Profiles).where(Profiles.user_id == current_user.id))
    if not profile:
        raise HTTPException(status_code=404, detail="Profil topilmadi...")

    profile.avatar_url = static_location
    await db.commit()
    return {"detail": "Avatar yuklandi...", "avatar_url": static_location}
