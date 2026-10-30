import pytest
import security
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


async def test_update_profile(auth_client: AsyncClient):
    response = await auth_client.put("/api/auth/me/profile", json={"full_name": "Ali Valiyev"})
    assert response.status_code == 200
    assert response.json()["profile"]["full_name"] == "Ali Valiyev"


async def test_upload_avatar(auth_client: AsyncClient):
    response = await auth_client.post("/api/auth/avatar", files={"file": ("rasm.png", b"fake", "image/png")})
    assert response.status_code == 200
    assert response.json()["avatar_url"] == "/uploads/avatars/1_avatar.png"
    assert (await auth_client.get("/uploads/avatars/1_avatar.png")).content == b"fake"

    me = await auth_client.get("/api/auth/me")
    assert me.json()["profile"]["avatar_url"] == "/uploads/avatars/1_avatar.png"


async def test_invalid_token(client: AsyncClient):
    client.headers["Authorization"] = "Bearer yaroqsiz"
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


async def test_token_without_sub(client: AsyncClient):
    token = security.create_access_token(data={})
    client.headers["Authorization"] = f"Bearer {token}"
    response = await client.get("/api/auth/me")
    assert response.status_code == 401
