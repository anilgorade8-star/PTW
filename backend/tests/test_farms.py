import pytest
import uuid
import httpx
from backend.app.core.config import settings

async def _register_user(client: httpx.AsyncClient, prefix: str):
    email = f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "FarmPassword@123"
    res = await client.post("/api/v1/auth/register", json={
        "name": f"{prefix} Farmer",
        "email": email,
        "password": pwd,
        "confirm_password": pwd
    })
    return res.cookies[settings.SESSION_COOKIE_NAME], res.json()["data"]["csrfToken"]

@pytest.mark.asyncio
async def test_farm_crud_and_ownership_authorization(client: httpx.AsyncClient):
    cookie_a, csrf_a = await _register_user(client, "alice")
    cookie_b, csrf_b = await _register_user(client, "bob")

    # 1. User A creates a farm
    farm_payload = {
        "name": "Green Valley Tomato Fields",
        "location": {
            "latitude": 18.5204,
            "longitude": 73.8567,
            "address": "Pune Rural Sector",
            "district": "Pune",
            "state": "Maharashtra"
        },
        "cropTypes": ["tomato"],
        "sizeInAcres": 3.5
    }

    create_res = await client.post(
        "/api/v1/farms",
        json=farm_payload,
        headers={"X-CSRF-Token": csrf_a},
        cookies={settings.SESSION_COOKIE_NAME: cookie_a}
    )
    assert create_res.status_code == 201, create_res.text
    farm_a_id = create_res.json()["data"]["id"]

    # 2. User A can view their farm
    view_res = await client.get(
        f"/api/v1/farms/{farm_a_id}",
        cookies={settings.SESSION_COOKIE_NAME: cookie_a}
    )
    assert view_res.status_code == 200
    assert view_res.json()["data"]["name"] == "Green Valley Tomato Fields"

    # 3. User B is DENIED viewing User A's farm (HTTP 403)
    b_view_res = await client.get(
        f"/api/v1/farms/{farm_a_id}",
        cookies={settings.SESSION_COOKIE_NAME: cookie_b}
    )
    assert b_view_res.status_code == 403
    assert b_view_res.json()["error"]["code"] == "FORBIDDEN"

    # 4. User B is DENIED modifying User A's farm (HTTP 403)
    b_patch_res = await client.patch(
        f"/api/v1/farms/{farm_a_id}",
        json={"name": "Hacked Farm"},
        headers={"X-CSRF-Token": csrf_b},
        cookies={settings.SESSION_COOKIE_NAME: cookie_b}
    )
    assert b_patch_res.status_code == 403

    # 5. User B is DENIED deleting User A's farm (HTTP 403)
    b_del_res = await client.delete(
        f"/api/v1/farms/{farm_a_id}",
        headers={"X-CSRF-Token": csrf_b},
        cookies={settings.SESSION_COOKIE_NAME: cookie_b}
    )
    assert b_del_res.status_code == 403

    # 6. User A successfully deletes their farm
    a_del_res = await client.delete(
        f"/api/v1/farms/{farm_a_id}",
        headers={"X-CSRF-Token": csrf_a},
        cookies={settings.SESSION_COOKIE_NAME: cookie_a}
    )
    assert a_del_res.status_code == 200
