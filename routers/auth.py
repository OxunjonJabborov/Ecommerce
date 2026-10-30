import security

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm

from enums import Roles
from database import get_db
from config import ADMIN_SECRET_KEY, AVATAR_FOLDER
from models import User, Profile
from dependencies import get_current_user
from storage import save_upload
from schemas.users import UserCreate, UserOut, ProfileUpdate, Token


auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])


async def resolve_role(user_in: UserCreate, db: AsyncSession) -> str:
    is_first_user = await db.scalar(select(func.count()).select_from(User)) == 0
    has_admin_secret = bool(user_in.admin_secret) and user_in.admin_secret == ADMIN_SECRET_KEY
    if is_first_user or has_admin_secret:
        return Roles.ADMIN.value
    return user_in.role.value


@auth_router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == user_in.email))
    if existing:
        raise HTTPException(status_code=400, detail="Bu email band...")

    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        role=await resolve_role(user_in, db),
        profile=Profile(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@auth_router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == form.username))
    if not user:
        raise HTTPException(status_code=400, detail="Email yoki parol noto'g'ri...")
    if not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Email yoki parol noto'g'ri...")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@auth_router.put("/me/profile", response_model=UserOut)
async def update_profile(data: ProfileUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.profile is None:
        current_user.profile = Profile()

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(current_user.profile, key, value)

    await db.commit()
    return current_user


@auth_router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.profile is None:
        raise HTTPException(status_code=404, detail="Profil topilmadi...")

    avatar_url = save_upload(file, AVATAR_FOLDER, f"{current_user.id}_avatar")
    current_user.profile.avatar_url = avatar_url
    await db.commit()
    return {"detail": "Avatar yuklandi...", "avatar_url": avatar_url}
