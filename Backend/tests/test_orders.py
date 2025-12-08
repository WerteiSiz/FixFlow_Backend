from fastapi.testclient import TestClient
from service_users.app.main import app as users_app
from service_orders.app.main import app as orders_app

users_client = TestClient(users_app)
orders_client = TestClient(orders_app)

def get_token():
    users_client.post("/v1/auth/register", json={"email":"o@test.com","password":"pass","name":"O"})
    r = users_client.post("/v1/auth/login", json={"email":"o@test.com","password":"pass","name":"O"})
    return r.json()["data"]["access_token"]

def test_create_and_get_order():
    token = get_token()
    r = orders_client.post("/v1/orders", json={"items":[{"product":"x","quantity":1}], "total": 10.0}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200 and r.json()["success"]
    order_id = r.json()["data"]["id"]
    r2 = orders_client.get(f"/v1/orders/{order_id}", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
