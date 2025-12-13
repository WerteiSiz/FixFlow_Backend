from fastapi.testclient import TestClient
from service_users.app.main import app as users_app
from service_orders.app.main import app as orders_app

users_client = TestClient(users_app)
orders_client = TestClient(orders_app)


def register_and_token(email: str):
    users_client.post("/v1/auth/register", json={"email": email, "password": "pw", "name": "U"})
    r = users_client.post("/v1/auth/login", json={"email": email, "password": "pw", "name": "U"})
    return r.json()["data"]["access_token"]


def test_order_pagination_and_forbidden_update_and_cancel():
    t1 = register_and_token("o1@test.com")
    t2 = register_and_token("o2@test.com")
    headers1 = {"Authorization": f"Bearer {t1}"}
    headers2 = {"Authorization": f"Bearer {t2}"}

    # create 3 orders for user1
    ids = []
    for i in range(3):
        r = orders_client.post("/v1/orders", json={"items": [{"sku": f"P{i}", "qty": 1, "price": 1.0}], "total": 1.0}, headers=headers1)
        assert r.status_code == 200 and r.json().get("success")
        ids.append(r.json()["data"]["id"])

    # pagination: limit=2
    r = orders_client.get("/v1/orders?limit=2&offset=0", headers=headers1)
    assert r.status_code == 200 and len(r.json()["data"]["items"]) == 2

    # user2 tries to update user1's order -> forbidden
    r = orders_client.patch(f"/v1/orders/{ids[0]}/status", json={"status": "completed"}, headers=headers2)
    assert r.status_code == 403

    # user1 cancels own order
    r = orders_client.delete(f"/v1/orders/{ids[0]}", headers=headers1)
    assert r.status_code == 200 and r.json()["data"]["status"] == "cancelled"
