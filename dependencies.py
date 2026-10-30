import jwt
import security

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from config import SECRET_KEY
from enums import Roles
from models import User
from database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz yoki muddati tugagan...",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await db.scalar(select(User).where(User.id == int(user_id)).options(selectinload(User.profile)))

    if user is None:
        raise credentials_exception
    return user


def role_checker(*allowed_roles: Roles):
    async def checker(user: User = Depends(get_current_user)):
        allowed_values = {role.value for role in allowed_roles}
        if user.role not in allowed_values:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat etilmagan... ")
        return user
    return checker
