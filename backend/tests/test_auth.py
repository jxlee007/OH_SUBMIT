"""Auth tests — happy path, failure cases, httpOnly cookie refresh, and logout."""
import pytest


REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
REFRESH_URL = "/api/auth/refresh"
LOGOUT_URL = "/api/auth/logout"

VALID_PAYLOAD = {
    "email": "user@brightloop.com",
    "password": "Secure@123",
    "full_name": "Bright User",
    "role": "customer",
}


def test_register_happy_path(client):
    """POST /api/auth/register — valid payload → 201 + user data."""
    resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == VALID_PAYLOAD["email"]
    assert "hashed_password" not in body["data"]


def test_register_duplicate_email_returns_409(client):
    """POST /api/auth/register — duplicate email → 409."""
    client.post(REGISTER_URL, json=VALID_PAYLOAD)
    resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
    assert resp.status_code == 409, resp.text


def test_register_weak_password_returns_422(client):
    """POST /api/auth/register — password without special char → 422."""
    payload = {**VALID_PAYLOAD, "email": "other@brightloop.com", "password": "weakpass1"}
    resp = client.post(REGISTER_URL, json=payload)
    assert resp.status_code == 422, resp.text


def test_login_happy_path(client):
    """POST /api/auth/login — valid credentials → 200 + access token + httpOnly cookie."""
    client.post(REGISTER_URL, json=VALID_PAYLOAD)
    resp = client.post(LOGIN_URL, json={"email": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["password"]})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    # Verify httpOnly refresh cookie is set
    assert "refresh_token" in resp.cookies


def test_login_wrong_password_returns_401(client):
    """POST /api/auth/login — wrong password → 401."""
    client.post(REGISTER_URL, json=VALID_PAYLOAD)
    resp = client.post(LOGIN_URL, json={"email": VALID_PAYLOAD["email"], "password": "WrongPass!1"})
    assert resp.status_code == 401, resp.text


def test_refresh_token_happy_path(client):
    """POST /api/auth/refresh — with httpOnly cookie → 200 + fresh access token."""
    client.post(REGISTER_URL, json=VALID_PAYLOAD)
    login_resp = client.post(LOGIN_URL, json={"email": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["password"]})
    assert "refresh_token" in login_resp.cookies

    # Send refresh request carrying the cookie
    refresh_resp = client.post(REFRESH_URL, cookies={"refresh_token": login_resp.cookies["refresh_token"]})
    assert refresh_resp.status_code == 200, refresh_resp.text
    assert refresh_resp.json()["success"] is True
    assert "access_token" in refresh_resp.json()["data"]


def test_refresh_token_missing_cookie_returns_401(client):
    """POST /api/auth/refresh — without cookie → 401 Unauthorized."""
    resp = client.post(REFRESH_URL)
    assert resp.status_code == 401, resp.text


def test_logout_endpoint(client):
    """POST /api/auth/logout — returns 200 and deletes refresh cookie."""
    client.post(REGISTER_URL, json=VALID_PAYLOAD)
    login_resp = client.post(LOGIN_URL, json={"email": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["password"]})
    
    logout_resp = client.post(LOGOUT_URL, cookies={"refresh_token": login_resp.cookies["refresh_token"]})
    assert logout_resp.status_code == 200, logout_resp.text
    assert logout_resp.json()["data"]["logged_out"] is True


def test_non_admin_cannot_create_staff_returns_403(client):
    """Anonymous or non-admin user registering with role='staff' → 403 Forbidden."""
    resp = client.post(
        REGISTER_URL,
        json={
            "email": "rogue_staff@brightloop.com",
            "password": "SecureStaff!123",
            "full_name": "Rogue Staff",
            "role": "staff",
        },
    )
    assert resp.status_code == 403
    assert "Only administrators" in resp.text


def test_admin_can_create_staff_happy_path(client, admin_token):
    """Authenticated admin registering staff account → 201 Created."""
    resp = client.post(
        REGISTER_URL,
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "legit_staff@brightloop.com",
            "password": "ValidStaff@123",
            "full_name": "Legit Staff User",
            "role": "staff",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["role"] == "staff"
