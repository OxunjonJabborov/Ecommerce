from pydantic import BaseModel, Field
from datetime import datetime


class TagBase(BaseModel):
    name: str = Field(max_length=50)


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class TagOut(TagBase):
    id: int
    model_config = {"from_attributes": True}


class CategoryBase(BaseModel):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=100)
    parent_id: int | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    slug: str | None = Field(None, max_length=100)
    parent_id: int | None = None


class CategoryOut(CategoryBase):
    id: int
    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    title: str = Field(max_length=255)
    description: str | None = None
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: int | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category_id: int | None = None


class ProductOut(ProductBase):
    id: int
    seller_id: int
    image_url: str | None = None
    created_at: datetime
    tags: list[TagOut] = []
    model_config = {"from_attributes": True}


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderItemOut(BaseModel):
    id: int
    order_id: int
    product_id: int | None
    quantity: int
    unit_price: float
    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: str | None = None


class OrderOut(BaseModel):
    id: int
    buyer_id: int
    status: str
    total_price: float
    created_at: datetime
    items: list[OrderItemOut] = []
    model_config = {"from_attributes": True}
