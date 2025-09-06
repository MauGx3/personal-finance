import json
import pytest

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient


User = get_user_model()


@pytest.mark.django_db
def test_assets_list_public_ok():
    client = APIClient()
    resp = client.get("/api/assets/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_create_asset_requires_authentication():
    client = APIClient()
    payload = {
        "symbol": "API1",
        "name": "API Asset",
    "asset_type": "STOCK",
        "currency": "USD",
    }
    resp = client.post("/api/assets/", payload, format="json")
    # default permission should require authentication for create
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_create_asset_authenticated():
    user = User.objects.create_user(username="apiuser", email="api@example.com", password="secret")
    client = APIClient()
    client.force_authenticate(user=user)
    payload = {
        "symbol": "API2",
        "name": "API Asset 2",
        "asset_type": "CRYPTO",
        "currency": "USD",
    }
    resp = client.post("/api/assets/", payload, format="json")
    assert resp.status_code == 201
    data = resp.json()
    assert data.get("symbol") == "API2"


@pytest.mark.django_db
def test_openapi_schema_includes_assets():
    # schema endpoint may be permissioned; use a staff user to fetch
    staff = User.objects.create_user(username="admin", email="admin@example.com", password="secret")
    staff.is_staff = True
    staff.save()
    client = APIClient()
    client.force_authenticate(user=staff)
    # Request JSON explicitly to ensure we receive a JSON payload
    resp = client.get("/api/schema/", HTTP_ACCEPT="application/json")
    assert resp.status_code == 200, f"schema fetch failed: {resp.status_code} - {resp.content}"
    content_type = resp.headers.get("Content-Type", "")
    # schema should be JSON or OpenAPI vendor type
    assert (
        "application/json" in content_type
        or "application/openapi+json" in content_type
        or "application/vnd.oai.openapi" in content_type
    )
    # Parse body as JSON regardless of Content-Type header
    payload = json.loads(resp.content.decode())
    paths = payload.get("paths", {})
    # Expect the assets base path to be present
    assert any(p.startswith("/api/assets") for p in paths)
