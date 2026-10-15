"""ExportIQ — Auth endpoint tests (register, login, /me)."""
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def unique_email():
    return f"test_{uuid.uuid4().hex[:12]}@example.com"


def register_user(email=None, password="Secure123", full_name="Test User"):
    if email is None:
        email = unique_email()
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    return response, email


def login_user(email, password="Secure123"):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


# ── Register ──────────────────────────────────────────────────────────────────

def test_register_success():
    response, email = register_user()
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] == "Test User"
    assert data["is_active"] is True
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email():
    email = unique_email()
    register_user(email=email)
    response, _ = register_user(email=email)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_weak_password():
    response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email(), "password": "short", "full_name": "Weak"},
    )
    assert response.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_success():
    _, email = register_user()
    response = login_user(email)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    _, email = register_user()
    response = login_user(email, password="WrongPass99")
    assert response.status_code == 401


def test_login_unknown_email():
    response = login_user("nobody@nowhere.invalid")
    assert response.status_code == 401


# ── /me ───────────────────────────────────────────────────────────────────────

def test_get_me():
    _, email = register_user()
    token = login_user(email).json()["access_token"]
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email


def test_get_me_no_token():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_bad_token():
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert response.status_code == 401
