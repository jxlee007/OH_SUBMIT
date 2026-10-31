"""Auth service — register, login, get_current_user."""
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from backend.app.core.database import get_db
from backend.app.core.security import hash_password, verify_password, decode_token
from backend.app.models.user import User
from backend.app.models.password_reset import PasswordResetToken
from backend.app.schemas.auth import RegisterRequest, LoginRequest
from backend.app.services.email_service import send_password_reset_email

bearer_scheme = HTTPBearer()


def register_user(payload: RegisterRequest, db: Session) -> User:
    """Register a new user. Raises 409 on duplicate email."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(payload: LoginRequest, db: Session) -> User:
    """Authenticate a user. Raises 401 on bad credentials."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if user.is_active != "Y":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency — decode JWT and return the authenticated user."""
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id: int = int(payload.get("sub"))
        token_version = payload.get("tv")
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    if token_version is not None and token_version != getattr(user, "token_version", 1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked due to credential change. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(*roles: str):
    """Dependency factory — enforces role-based access control."""
    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {', '.join(roles)}",
            )
        return current_user
    return _checker


def request_password_reset(email: str, db: Session) -> None:
    """Dispatches password reset link. Anti-enumeration: returns identically if email not found."""
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        return

    plain_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

    reset_rec = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        used=False,
    )
    db.add(reset_rec)
    db.commit()

    send_password_reset_email(user.email, plain_token)


def complete_password_reset(token: str, new_password: str, db: Session) -> User:
    """Completes password reset, increments token_version to invalidate active sessions."""
    token_hash = hashlib.sha256(token.strip().encode()).hexdigest()
    reset_rec = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()
    if not reset_rec or reset_rec.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid or has already been used.",
        )

    exp = reset_rec.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired.",
        )

    user = db.query(User).filter(User.id == reset_rec.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    user.hashed_password = hash_password(new_password)
    user.token_version = getattr(user, "token_version", 1) + 1
    reset_rec.used = True
    db.commit()
    db.refresh(user)
    return user
