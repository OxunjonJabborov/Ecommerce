import os

# Ilova modullari import qilinishidan oldin o'rnatilishi shart
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ.setdefault("SECRET_KEY", "test-secret-key-faqat-testlar-uchun-32-belgi")

import pytest_asyncio  # noqa: E402
from httpx import AsyncClient, ASGITransport  # noqa: E402

from main import app  # noqa: E402
from database import Base, engine  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client):
    await client.post("/api/auth/register", json={
        "email": "admin@test.com",
        "password": "test1234",
    })
    response = await client.post("/api/auth/login", data={
        "username": "admin@test.com",
        "password": "test1234",
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest_asyncio.fixture
async def login_as(client):
    """Foydalanuvchini ro'yxatdan o'tkazib, client'ga uning tokenini o'rnatadi."""
    async def _login_as(email: str, role: str | None = None) -> AsyncClient:
        body = {"email": email, "password": "test1234"}
        if role:
            body["role"] = role
        await client.post("/api/auth/register", json=body)
        response = await client.post("/api/auth/login", data={"username": email, "password": "test1234"})
        client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
        return client
    return _login_as
