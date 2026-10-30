import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_admin_lists_users(auth_client: AsyncClient):
    response = await auth_client.get("/api/admins/users")
    assert response.status_code == 200
    assert [u["email"] for u in response.json()] == ["admin@test.com"]


async def test_admin_updates_role(login_as):
    client = await login_as("admin@test.com")
    await client.post("/api/auth/register", json={"email": "user@test.com", "password": "test1234"})

    response = await client.put("/api/admins/users/2/role", params={"new_role": "seller"})
    assert response.status_code == 200
    assert response.json()["role"] == "seller"


async def test_admin_update_role_unknown_user(auth_client: AsyncClient):
    response = await auth_client.put("/api/admins/users/999/role", params={"new_role": "seller"})
    assert response.status_code == 404


async def test_admin_deletes_user(login_as):
    client = await login_as("admin@test.com")
    await client.post("/api/auth/register", json={"email": "user@test.com", "password": "test1234"})

    response = await client.delete("/api/admins/users/2")
    assert response.status_code == 200
    assert response.json()["detail"] == "user@test.com o'chirildi..."


async def test_admin_delete_unknown_user(auth_client: AsyncClient):
    response = await auth_client.delete("/api/admins/users/999")
    assert response.status_code == 404


async def test_non_admin_cannot_list_users(login_as):
    await login_as("admin@test.com")
    client = await login_as("buyer@test.com")
    response = await client.get("/api/admins/users")
    assert response.status_code == 403


async def test_requires_token(client: AsyncClient):
    response = await client.get("/api/admins/users")
    assert response.status_code == 401
