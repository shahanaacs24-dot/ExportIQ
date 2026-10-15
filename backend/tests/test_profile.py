"""ExportIQ — MSME Profile endpoint tests (create, get, update)."""
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def unique_email():
    return f"prof_{uuid.uuid4().hex[:12]}@example.com"


def create_and_login():
    """Register a fresh user and return an auth header dict."""
    email = unique_email()
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Secure123", "full_name": "Profile Tester"},
    )
    token = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "Secure123"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


PROFILE_PAYLOAD = {
    "business_name": "TestCo Exports",
    "state": "Maharashtra",
    "city": "Mumbai",
    "has_exported_before": False,
}


# ── GET profile (none yet) ────────────────────────────────────────────────────

def test_get_profile_not_found():
    headers = create_and_login()
    response = client.get("/api/v1/profile", headers=headers)
    assert response.status_code == 404


# ── POST create profile ───────────────────────────────────────────────────────

def test_create_profile_success():
    headers = create_and_login()
    response = client.post("/api/v1/profile", json=PROFILE_PAYLOAD, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["business_name"] == "TestCo Exports"
    assert data["city"] == "Mumbai"
    assert "id" in data
    assert "user_id" in data


def test_create_profile_duplicate():
    headers = create_and_login()
    client.post("/api/v1/profile", json=PROFILE_PAYLOAD, headers=headers)
    response = client.post("/api/v1/profile", json=PROFILE_PAYLOAD, headers=headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_create_profile_unauthenticated():
    response = client.post("/api/v1/profile", json=PROFILE_PAYLOAD)
    assert response.status_code == 401


# ── GET profile (after create) ────────────────────────────────────────────────

def test_get_profile_after_create():
    headers = create_and_login()
    client.post("/api/v1/profile", json=PROFILE_PAYLOAD, headers=headers)
    response = client.get("/api/v1/profile", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["business_name"] == "TestCo Exports"


# ── PATCH update profile ──────────────────────────────────────────────────────

def test_update_profile_success():
    headers = create_and_login()
    client.post("/api/v1/profile", json=PROFILE_PAYLOAD, headers=headers)
    response = client.patch(
        "/api/v1/profile",
        json={"city": "Pune", "has_exported_before": True},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Pune"
    assert data["has_exported_before"] is True
    # unchanged fields persist
    assert data["business_name"] == "TestCo Exports"


def test_update_profile_not_found():
    headers = create_and_login()
    response = client.patch(
        "/api/v1/profile",
        json={"city": "Delhi"},
        headers=headers,
    )
    assert response.status_code == 404
