import pytest
import uuid
import httpx
from backend.app.core.config import settings

@pytest.mark.asyncio
async def test_registration_and_login_flow(client: httpx.AsyncClient):
    random_str = uuid.uuid4().hex[:8]
    email = f"farmer_{random_str}@example.com"
    password = "StrongPassword@123"

    # 1. Register
    reg_payload = {
        "name": "Ramesh Kumar",
        "email": email,
        "password": password,
        "confirm_password": password
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 200, reg_res.text
    reg_data = reg_res.json()
    assert reg_data["success"] is True
    assert reg_data["data"]["user"]["email"] == email
    assert "csrfToken" in reg_data["data"]
    assert settings.SESSION_COOKIE_NAME in reg_res.cookies

    # 2. Duplicate registration rejection
    dup_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 409
    assert dup_res.json()["error"]["code"] == "CONFLICT"

    # 3. Logout
    logout_res = await client.post(
        "/api/v1/auth/logout",
        cookies={settings.SESSION_COOKIE_NAME: reg_res.cookies[settings.SESSION_COOKIE_NAME]}
    )
    assert logout_res.status_code == 200

    # 4. Login with invalid password
    bad_login = await client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword!"})
    assert bad_login.status_code == 401
    assert "Invalid email or password" in bad_login.json()["error"]["message"]

    # 5. Login with correct password
    good_login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert good_login.status_code == 200
    login_data = good_login.json()
    assert login_data["success"] is True
    session_cookie = good_login.cookies[settings.SESSION_COOKIE_NAME]
    csrf_token = login_data["data"]["csrfToken"]

    # 6. Verify /auth/me
    me_res = await client.get("/api/v1/auth/me", cookies={settings.SESSION_COOKIE_NAME: session_cookie})
    assert me_res.status_code == 200
    assert me_res.json()["data"]["user"]["email"] == email

    # 7. Password change requiring CSRF
    change_no_csrf = await client.post(
        "/api/v1/auth/password/change",
        json={"current_password": password, "new_password": "NewStrongPass@456", "confirm_password": "NewStrongPass@456"},
        cookies={settings.SESSION_COOKIE_NAME: session_cookie}
    )
    assert change_no_csrf.status_code == 403  # Blocked by CSRF

    # Password change with valid CSRF
    change_with_csrf = await client.post(
        "/api/v1/auth/password/change",
        json={"current_password": password, "new_password": "NewStrongPass@456", "confirm_password": "NewStrongPass@456"},
        headers={"X-CSRF-Token": csrf_token},
        cookies={settings.SESSION_COOKIE_NAME: session_cookie}
    )
    assert change_with_csrf.status_code == 200
    assert change_with_csrf.json()["data"] is True
