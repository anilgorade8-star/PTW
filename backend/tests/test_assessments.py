import io
import uuid
import pytest
import httpx
from PIL import Image
from backend.app.core.config import settings

def _generate_test_image(color="green", width=200, height=200) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

async def _register_farmer_with_farm(client: httpx.AsyncClient):
    email = f"farmer_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "FarmPassword@123"
    reg = await client.post("/api/v1/auth/register", json={
        "name": "Kisan Bhai",
        "email": email,
        "password": pwd,
        "confirm_password": pwd
    })
    cookie = reg.cookies[settings.SESSION_COOKIE_NAME]
    csrf = reg.json()["data"]["csrfToken"]

    farm_res = await client.post(
        "/api/v1/farms",
        json={
            "name": "Nashik Tomato Field",
            "location": {"latitude": 19.9975, "longitude": 73.7898, "district": "Nashik", "state": "Maharashtra"},
            "cropTypes": ["tomato"],
            "sizeInAcres": 2.0
        },
        headers={"X-CSRF-Token": csrf},
        cookies={settings.SESSION_COOKIE_NAME: cookie}
    )
    farm_id = farm_res.json()["data"]["id"]
    return cookie, csrf, farm_id

@pytest.mark.asyncio
async def test_assessment_creation_and_followup(client: httpx.AsyncClient):
    cookie, csrf, farm_id = await _register_farmer_with_farm(client)

    # 1. Invalid file upload (not an image)
    bad_upload = await client.post(
        "/api/v1/assessments",
        data={"farmId": farm_id, "cropType": "tomato", "growthStage": "vegetative"},
        files={"image": ("text.txt", b"This is a long plain text file that is not a JPEG, PNG, or WebP image at all and contains more than one hundred bytes." * 2, "text/plain")},
        cookies={settings.SESSION_COOKIE_NAME: cookie}
    )
    assert bad_upload.status_code == 422
    assert "Invalid image format" in bad_upload.json()["error"]["message"]

    # 2. Valid image upload
    img_bytes = _generate_test_image()
    good_upload = await client.post(
        "/api/v1/assessments",
        data={
            "farmId": farm_id,
            "cropType": "tomato",
            "growthStage": "vegetative",
            "symptoms": "dark concentric spots on lower leaves, yellow ring"
        },
        files={"image": ("tomato_leaf.jpg", img_bytes, "image/jpeg")},
        cookies={settings.SESSION_COOKIE_NAME: cookie}
    )
    assert good_upload.status_code == 202
    assessment_data = good_upload.json()["data"]
    assessment_id = assessment_data["id"]
    assert assessment_data["cropType"] == "tomato"
    assert assessment_data["farmId"] == farm_id

    # 3. Retrieve assessment
    detail_res = await client.get(
        f"/api/v1/assessments/{assessment_id}",
        cookies={settings.SESSION_COOKIE_NAME: cookie}
    )
    assert detail_res.status_code == 200
    detail = detail_res.json()["data"]
    assert detail["status"] in ["queued", "processing", "completed", "awaiting_farmer_input"]
    assert "imageUrl" in detail

    # 4. List assessments
    list_res = await client.get(
        "/api/v1/assessments",
        cookies={settings.SESSION_COOKIE_NAME: cookie}
    )
    assert list_res.status_code == 200
    items = list_res.json()["data"]["items"]
    assert any(item["id"] == assessment_id for item in items)

    # 5. Submit follow-up response
    followup_res = await client.post(
        f"/api/v1/assessments/{assessment_id}/followups",
        json={"answer": "Yes, target bullseye rings are clearly on the lowest 3 leaf branches."},
        headers={"X-CSRF-Token": csrf},
        cookies={settings.SESSION_COOKIE_NAME: cookie}
    )
    assert followup_res.status_code == 200
    updated_detail = followup_res.json()["data"]
    assert len(updated_detail["followups"]) >= 1
    assert "Yes, target bullseye rings" in updated_detail["followups"][-1]["answer"]
