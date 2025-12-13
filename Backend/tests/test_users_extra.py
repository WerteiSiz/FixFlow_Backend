from fastapi.testclient import TestClient
from service_users.app.main import app as users_app

client = TestClient(users_app)


def test_duplicate_registration():
    payload = {"email": "dup@test.com", "password": "passwd", "name": "Dup"}
    r1 = client.post("/v1/auth/register", json=payload)
    assert r1.status_code == 200 and r1.json().get("success")
    r2 = client.post("/v1/auth/register", json=payload)
    assert r2.status_code == 400


def test_protected_endpoint_requires_token():
    r = client.get("/v1/users/me")
    assert r.status_code == 401
