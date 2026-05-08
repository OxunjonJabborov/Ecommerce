import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_seller_create_product(client: AsyncClient):
    # seller ro'yxatdan o'tish
    await client.post("/api/auth/register", json={
        "email": "admin@test.com", "password": "test1234"
    })
    await client.post("/api/auth/register", json={
        "email": "seller@test.com", "password": "test1234", "role": "seller"
    })
    login = await client.post("/api/auth/login", data={
        "username": "seller@test.com", "password": "test1234"
    })
    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    response = await client.post("/api/seller/products", json={
        "title": "Test mahsulot",
        "price": 99.9,
        "stock": 10,
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Test mahsulot"


async def test_buyer_cannot_create_product(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "admin@test.com", "password": "test1234"
    })
    await client.post("/api/auth/register", json={
        "email": "buyer@test.com", "password": "test1234"
    })
    login = await client.post("/api/auth/login", data={
        "username": "buyer@test.com", "password": "test1234"
    })
    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    response = await client.post("/api/seller/products", json={
        "title": "Test", "price": 10.0, "stock": 5
    })
    assert response.status_code == 403


async def test_seller_cannot_delete_others_product(client: AsyncClient):
    # birinchi seller
    await client.post("/api/auth/register", json={
        "email": "admin@test.com", "password": "test1234"
    })
    await client.post("/api/auth/register", json={
        "email": "seller1@test.com", "password": "test1234", "role": "seller"
    })
    login1 = await client.post("/api/auth/login", data={
        "username": "seller1@test.com", "password": "test1234"
    })
    client.headers["Authorization"] = f"Bearer {login1.json()['access_token']}"
    product = await client.post("/api/seller/products", json={
        "title": "Seller1 mahsuloti", "price": 50.0, "stock": 5
    })
    product_id = product.json()["id"]

    # ikkinchi seller
    await client.post("/api/auth/register", json={
        "email": "seller2@test.com", "password": "test1234", "role": "seller"
    })
    login2 = await client.post("/api/auth/login", data={
        "username": "seller2@test.com", "password": "test1234"
    })
    client.headers["Authorization"] = f"Bearer {login2.json()['access_token']}"

    response = await client.delete(f"/api/seller/products/{product_id}")
    assert response.status_code == 403
