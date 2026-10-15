"""ExportIQ — Products and destinations endpoint tests (read-only, seeded data)."""
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def unique_email():
    return f"prod_{uuid.uuid4().hex[:12]}@example.com"


def get_auth_headers():
    """Register a fresh user and return auth headers."""
    email = unique_email()
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Secure123", "full_name": "Products Tester"},
    )
    token = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "Secure123"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Products ──────────────────────────────────────────────────────────────────

def test_list_products_unauthenticated():
    response = client.get("/api/v1/products")
    assert response.status_code == 401


def test_list_products_authenticated():
    headers = get_auth_headers()
    response = client.get("/api/v1/products", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Seed data has 8 products
    assert len(data) >= 1
    # Check schema fields
    first = data[0]
    assert "id" in first
    assert "hs_code" in first
    assert "name" in first


def test_list_products_search_match():
    headers = get_auth_headers()
    # All seeded products should be returned when no filter applied
    all_products = client.get("/api/v1/products", headers=headers).json()
    if not all_products:
        return  # nothing to search

    # Use first product's name fragment as search term
    name_fragment = all_products[0]["name"][:4]
    response = client.get(f"/api/v1/products?q={name_fragment}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Every result name or hs_code should contain the fragment (case-insensitive)
    for item in data:
        match = (
            name_fragment.lower() in item["name"].lower()
            or name_fragment.lower() in item["hs_code"].lower()
        )
        assert match


def test_list_products_search_no_match():
    headers = get_auth_headers()
    response = client.get("/api/v1/products?q=XYZNOTEXIST99999", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


# ── Destinations ──────────────────────────────────────────────────────────────

def test_list_destinations_unauthenticated():
    response = client.get("/api/v1/products/destinations")
    assert response.status_code == 401


def test_list_destinations_authenticated():
    headers = get_auth_headers()
    response = client.get("/api/v1/products/destinations", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Seed data has 10 countries
    assert len(data) >= 1
    first = data[0]
    assert "id" in first
    assert "iso_code" in first
    assert "name" in first


def test_list_destinations_search_match():
    headers = get_auth_headers()
    all_dest = client.get("/api/v1/products/destinations", headers=headers).json()
    if not all_dest:
        return

    name_fragment = all_dest[0]["name"][:3]
    response = client.get(
        f"/api/v1/products/destinations?q={name_fragment}", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        match = (
            name_fragment.lower() in item["name"].lower()
            or name_fragment.lower() in item["iso_code"].lower()
        )
        assert match


def test_list_destinations_search_no_match():
    headers = get_auth_headers()
    response = client.get(
        "/api/v1/products/destinations?q=XYZNOTEXIST99999", headers=headers
    )
    assert response.status_code == 200
    assert response.json() == []
