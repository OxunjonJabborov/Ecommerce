from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enums import RegisterRoles, Roles


class ProfileOut(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    address: str | None = None
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    address: str | None = Field(None, max_length=255)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: RegisterRoles = RegisterRoles.BUYER
    admin_secret: str | None = None


class UserOut(BaseModel):
    id: int
    email: str
    role: Roles
    created_at: datetime
    profile: ProfileOut | None = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
