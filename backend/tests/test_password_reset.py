"""Tests for self-service password reset flow and session revocation."""
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from backend.app.models.user import User
from backend.app.models.password_reset import PasswordResetToken
from backend.app.core.security import hash_password


def test_forgot_password_unknown_email_returns_200(client: TestClient):
    """Anti-enumeration: returns identical 200 response when email is not registered."""
    res = client.post("/api/auth/forgot-password", json={"email": "nonexistent@nowhere.com"})
    assert res.status_code == 200
    assert res.json()["data"]["dispatched"] is True


def test_reset_password_weak_password_returns_422(client: TestClient):
    """Enforces 3-layer validation password policy."""
    res = client.post(
        "/api/auth/reset-password",
        json={"token": "some-token-string", "new_password": "weak"},
    )
    assert res.status_code == 422
    assert "at least 8 characters" in res.text


def test_reset_password_expired_token_returns_400(client: TestClient, db_session):
    user = User(
        email="reset_exp@test.com",
        hashed_password=hash_password("OldPassword@123"),
        full_name="Exp Reset User",
        role="customer",
    )
    db_session.add(user)
    db_session.flush()

    raw_token = "expired_raw_token_12345"
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expired_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        used=False,
    )
    db_session.add(expired_token)
    db_session.commit()

    res = client.post(
        "/api/auth/reset-password",
        json={"token": raw_token, "new_password": "NewValidPass@123"},
    )
    assert res.status_code == 400
    assert "expired" in res.text.lower()


def test_reset_password_reused_token_returns_400(client: TestClient, db_session):
    user = User(
        email="reset_reused@test.com",
        hashed_password=hash_password("OldPassword@123"),
        full_name="Reused Reset User",
        role="customer",
    )
    db_session.add(user)
    db_session.flush()

    raw_token = "already_used_token_12345"
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    used_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=25),
        used=True,  # already used
    )
    db_session.add(used_token)
    db_session.commit()

    res = client.post(
        "/api/auth/reset-password",
        json={"token": raw_token, "new_password": "NewValidPass@123"},
    )
    assert res.status_code == 400
    assert "already been used" in res.text.lower() or "invalid" in res.text.lower()


def test_reset_password_happy_path_and_relogin(client: TestClient, db_session):
    user = User(
        email="reset_happy@test.com",
        hashed_password=hash_password("InitialPassword@123"),
        full_name="Happy Reset User",
        role="customer",
    )
    db_session.add(user)
    db_session.flush()

    raw_token = "valid_happy_token_99999"
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    reset_rec = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=20),
        used=False,
    )
    db_session.add(reset_rec)
    db_session.commit()

    # 1. Reset password
    res = client.post(
        "/api/auth/reset-password",
        json={"token": raw_token, "new_password": "BrandNewSecret@123"},
    )
    assert res.status_code == 200

    # 2. Old password should fail
    old_login = client.post(
        "/api/auth/login",
        json={"email": "reset_happy@test.com", "password": "InitialPassword@123"},
    )
    assert old_login.status_code == 401

    # 3. New password should succeed
    new_login = client.post(
        "/api/auth/login",
        json={"email": "reset_happy@test.com", "password": "BrandNewSecret@123"},
    )
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()["data"]


def test_reset_password_invalidates_prior_active_tokens(client: TestClient, db_session):
    """Tests session revocation: old access tokens issued before password reset are rejected."""
    user = User(
        email="session_revoke@test.com",
        hashed_password=hash_password("OriginalPass@123"),
        full_name="Session Revoke User",
        role="customer",
        token_version=1,
    )
    db_session.add(user)
    db_session.commit()

    # Login and obtain access token with tv=1
    login_res = client.post(
        "/api/auth/login",
        json={"email": "session_revoke@test.com", "password": "OriginalPass@123"},
    )
    assert login_res.status_code == 200
    old_access_token = login_res.json()["data"]["access_token"]

    # Generate reset token and reset password
    raw_token = "session_kill_token_11111"
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    reset_rec = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        used=False,
    )
    db_session.add(reset_rec)
    db_session.commit()

    res = client.post(
        "/api/auth/reset-password",
        json={"token": raw_token, "new_password": "UpdatedPassword@123"},
    )
    assert res.status_code == 200

    # Prior access token should now be rejected with 401 Unauthorized
    verify_old = client.get(
        "/api/products",
        headers={"Authorization": f"Bearer {old_access_token}"},
    )
    assert verify_old.status_code == 401
    assert "revoked" in verify_old.text.lower() or "invalid" in verify_old.text.lower()
