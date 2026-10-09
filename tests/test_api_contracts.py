from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}

def test_full_auth_and_audit_contract(client: TestClient):
    # 1. Register User
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={"email": "operator@enterprise.com", "password": "SecurePassword123!"},
    )
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["email"] == "operator@enterprise.com"
    assert user_data["role"] == "member"

    # 2. Login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "operator@enterprise.com", "password": "SecurePassword123!"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Access Protected Profile
    profile_resp = client.get("/api/v1/users/me", headers=headers)
    assert profile_resp.status_code == 200
    assert profile_resp.json()["email"] == "operator@enterprise.com"

    # 4. Create Audit Log
    audit_resp = client.post(
        "/api/v1/audit",
        headers=headers,
        json={"action": "ORDER_PLACED", "details": "Invoice #88439 generated"},
    )
    assert audit_resp.status_code == 201
    assert audit_resp.json()["action"] == "ORDER_PLACED"

    # 5. Retrieve Logs
    list_resp = client.get("/api/v1/audit", headers=headers)
    assert list_resp.status_code == 200
    logs = list_resp.json()
    assert len(logs) == 1
    assert logs[0]["action"] == "ORDER_PLACED"

def test_unauthorized_access_rejection(client: TestClient):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401
