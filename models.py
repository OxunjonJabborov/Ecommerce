from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(length=100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(length=255))
    role: Mapped[str] = mapped_column(Enum("admin", "seller", "buyer"), default="buyer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    profile: Mapped["Profiles"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    products: Mapped[list["Products"]] = relationship(back_populates="seller", cascade="all, delete-orphan")
    orders: Mapped[list["Orders"]] = relationship(back_populates="buyer", cascade="all, delete-orphan")


class Profiles(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    full_name: Mapped[str | None] = mapped_column(String(length=100))
    phone: Mapped[str | None] = mapped_column(String(length=20))
    address: Mapped[str | None] = mapped_column(String(length=255))
    avatar_url: Mapped[str | None] = mapped_column(String(length=500))

    user: Mapped["Users"] = relationship(back_populates="profile")


class Categories(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(length=100))
    slug: Mapped[str] = mapped_column(String(length=100), unique=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    products: Mapped[list["Products"]] = relationship(back_populates="category", cascade="all, delete-orphan")
    children: Mapped[list["Categories"]] = relationship(back_populates="parent")
    parent: Mapped["Categories | None"] = relationship(back_populates="children", remote_side="Categories.id")


class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(length=255))
    description: Mapped[str | None] = mapped_column(Text)  # Mapped[Text] xato edi, Mapped[str] to'g'ri
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str | None] = mapped_column(String(length=500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    seller: Mapped["Users"] = relationship(back_populates="products")
    category: Mapped["Categories | None"] = relationship(back_populates="products")
    tags: Mapped[list["Tags"]] = relationship(secondary="product_tags", back_populates="products")
    order_items: Mapped[list["OrderItems"]] = relationship(back_populates="product")


class Tags(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(length=50), unique=True)

    products: Mapped[list["Products"]] = relationship(secondary="product_tags", back_populates="tags")


class ProductTags(Base):
    __tablename__ = "product_tags"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(Enum("pending", "paid", "shipped", "cancelled"), default="pending")
    total_price: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    buyer: Mapped["Users"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItems"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItems(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)  # sotib olingan paytdagi narx

    order: Mapped["Orders"] = relationship(back_populates="items")
    product: Mapped["Products | None"] = relationship(back_populates="order_items")
