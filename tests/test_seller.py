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


async def test_seller_updates_own_product(login_as):
    await login_as("admin@test.com")
    client = await login_as("seller@test.com", role="seller")
    product = await client.post("/api/seller/products", json={"title": "Eski", "price": 10.0})

    response = await client.put(f"/api/seller/products/{product.json()['id']}", json={"title": "Yangi"})
    assert response.status_code == 200
    assert response.json()["title"] == "Yangi"
    assert response.json()["price"] == 10.0


async def test_seller_deletes_own_product(login_as):
    await login_as("admin@test.com")
    client = await login_as("seller@test.com", role="seller")
    product = await client.post("/api/seller/products", json={"title": "Test", "price": 10.0})

    response = await client.delete(f"/api/seller/products/{product.json()['id']}")
    assert response.status_code == 200
    assert (await client.get("/api/products")).json() == []


async def test_admin_can_update_any_product(login_as):
    await login_as("admin@test.com")
    seller = await login_as("seller@test.com", role="seller")
    product = await seller.post("/api/seller/products", json={"title": "Test", "price": 10.0})

    admin = await login_as("admin@test.com")
    response = await admin.put(f"/api/seller/products/{product.json()['id']}", json={"stock": 7})
    assert response.status_code == 200
    assert response.json()["stock"] == 7


async def test_update_unknown_product(auth_client):
    response = await auth_client.put("/api/seller/products/999", json={"title": "X"})
    assert response.status_code == 404


async def test_upload_product_image(auth_client):
    product = await auth_client.post("/api/seller/products", json={"title": "Test", "price": 10.0})
    product_id = product.json()["id"]

    response = await auth_client.post(
        f"/api/seller/products/{product_id}/image",
        files={"file": ("rasm.jpg", b"fake", "image/jpeg")},
    )
    assert response.status_code == 200
    image_url = response.json()["image_url"]
    assert image_url.startswith("/uploads/products/") and image_url.endswith(".jpg")
    assert (await auth_client.get(f"/api/products/{product_id}")).json()["image_url"] == image_url
