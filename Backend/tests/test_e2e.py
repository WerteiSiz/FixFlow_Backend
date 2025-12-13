from fastapi import FastAPI
from fastapi.testclient import TestClient

from api_gateway.app.main import app as gateway_app
from api_gateway.app import main as gateway_main
from api_gateway.app import config as gateway_config
from service_users.app.main import app as users_app
from service_orders.app.main import app as orders_app


def test_e2e_register_login_create_order_and_propagation():
    composite = FastAPI()
    composite.mount("/v1", gateway_app)
    composite.mount("/users", users_app)
    composite.mount("/orders", orders_app)

    gateway_config.settings.USERS_URL = "http://testserver/users/v1"
    gateway_config.settings.ORDERS_URL = "http://testserver/orders/v1"

  
    from httpx import AsyncClient, ASGITransport
    import asyncio

    transport = ASGITransport(app=composite)
    gateway_main.async_client = AsyncClient(transport=transport, base_url="http://testserver")

    async def run_sequence():
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Register
            r = await client.post("/v1/users/auth/register", json={"email": "e2e@test.com", "password": "pass", "name": "E2E"})
            assert r.status_code == 200 and r.json().get("success")

            # Login
            r = await client.post("/v1/users/auth/login", json={"email": "e2e@test.com", "password": "pass", "name": "E2E"})
            assert r.status_code == 200 and r.json().get("success")
            token = r.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Create order via gateway
            payload = {"items": [{"sku": "X1", "qty": 2, "price": 5.0}], "total": 10.0}
            r = await client.post("/v1/orders/orders", json=payload, headers=headers)
            assert r.status_code == 200 and r.json().get("success")
            order_id = r.json()["data"]["id"]

            # Get order and check X-Request-ID propagation header present
            r2 = await client.get(f"/v1/orders/orders/{order_id}", headers=headers)
            assert r2.status_code == 200
            assert r2.headers.get("X-Request-ID") is not None

    asyncio.run(run_sequence())
