from fastapi.testclient import TestClient
from service_users.app.main import app as users_app

client = TestClient(users_app)

def test_register_and_login():
    r = client.post("/v1/auth/register", json={"email":"t@test.com","password":"passw0rd","name":"T"})
    assert r.status_code == 200 and r.json()["success"]
    r2 = client.post("/v1/auth/login", json={"email":"t@test.com","password":"passw0rd","name":"T"})
    assert r2.status_code == 200 and r2.json()["success"]
    token = r2.json()["data"]["access_token"]
    r3 = client.get("/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200 and r3.json()["data"]["email"] == "t@test.com"
