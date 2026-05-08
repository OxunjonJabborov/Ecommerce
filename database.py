import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL muhit o'zgaruvchisi aniqlanmagan...")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_async_engine(DATABASE_URL, connect_args=connect_args, echo=True)

async_session = async_sessionmaker(bind=engine, autoflush=True)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session
