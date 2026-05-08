import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "email": "user@test.com",
        "password": "test1234",
    })
    assert response.status_code == 200
    assert response.json()["email"] == "user@test.com"


async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "user@test.com",
        "password": "test1234",
    })
    response = await client.post("/api/auth/register", json={
        "email": "user@test.com",
        "password": "test1234",
    })
    assert response.status_code == 400
    assert "band" in response.json()["detail"]


async def test_login_success(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "user@test.com",
        "password": "test1234",
    })
    response = await client.post("/api/auth/login", data={
        "username": "user@test.com",
        "password": "test1234",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "user@test.com",
        "password": "test1234",
    })
    response = await client.post("/api/auth/login", data={
        "username": "user@test.com",
        "password": "NOTO'G'RI_PAROL",
    })
    assert response.status_code == 400


async def test_first_user_is_admin(client: AsyncClient):
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

    me = await client.get("/api/auth/me")
    assert me.json()["role"] == "admin"
