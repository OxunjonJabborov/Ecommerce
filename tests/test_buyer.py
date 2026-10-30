import pytest

pytestmark = pytest.mark.asyncio


async def create_product(client, title="Olma", price=10.0, stock=5) -> int:
    response = await client.post("/api/seller/products", json={"title": title, "price": price, "stock": stock})
    return response.json()["id"]


async def test_list_and_get_products(login_as):
    client = await login_as("admin@test.com")
    product_id = await create_product(client)

    products = await client.get("/api/products")
    assert products.status_code == 200
    assert [p["title"] for p in products.json()] == ["Olma"]

    product = await client.get(f"/api/products/{product_id}")
    assert product.status_code == 200
    assert product.json()["tags"] == []


async def test_get_unknown_product(client):
    response = await client.get("/api/products/999")
    assert response.status_code == 404


async def test_order_with_multiple_items(login_as):
    client = await login_as("admin@test.com")
    apple = await create_product(client, "Olma", 10.0, 5)
    pear = await create_product(client, "Nok", 20.0, 5)

    response = await client.post("/api/orders", json={"items": [
        {"product_id": apple, "quantity": 2},
        {"product_id": pear, "quantity": 1},
    ]})
    assert response.status_code == 200
    order = response.json()
    assert order["total_price"] == 40.0
    assert len(order["items"]) == 2

    stock = {p["id"]: p["stock"] for p in (await client.get("/api/products")).json()}
    assert stock == {apple: 3, pear: 4}


async def test_order_insufficient_stock(login_as):
    client = await login_as("admin@test.com")
    product_id = await create_product(client, stock=1)

    response = await client.post("/api/orders", json={"items": [{"product_id": product_id, "quantity": 2}]})
    assert response.status_code == 400


async def test_order_unknown_product(auth_client):
    response = await auth_client.post("/api/orders", json={"items": [{"product_id": 999, "quantity": 1}]})
    assert response.status_code == 404


async def test_seller_cannot_order(login_as):
    await login_as("admin@test.com")
    client = await login_as("seller@test.com", role="seller")
    response = await client.post("/api/orders", json={"items": []})
    assert response.status_code == 403


async def test_my_orders(login_as):
    client = await login_as("admin@test.com")
    product_id = await create_product(client)
    await client.post("/api/orders", json={"items": [{"product_id": product_id, "quantity": 1}]})

    response = await client.get("/api/orders/my")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert len(response.json()[0]["items"]) == 1
