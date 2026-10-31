"""Auth tests — happy path and failure cases."""
import pytest


REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"

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
    """POST /api/auth/login — valid credentials → 200 + access token."""
    client.post(REGISTER_URL, json=VALID_PAYLOAD)
    resp = client.post(LOGIN_URL, json={"email": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["password"]})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]


def test_login_wrong_password_returns_401(client):
    """POST /api/auth/login — wrong password → 401."""
    client.post(REGISTER_URL, json=VALID_PAYLOAD)
    resp = client.post(LOGIN_URL, json={"email": VALID_PAYLOAD["email"], "password": "WrongPass!1"})
    assert resp.status_code == 401, resp.text
