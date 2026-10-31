"""Auth routes — registration, login, cookie-based refresh, and logout."""
from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import create_access_token, create_refresh_token, decode_token
from backend.app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from backend.app.schemas.common import StandardResponse, ok
from backend.app.services.auth_service import register_user, login_user
from backend.app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

REFRESH_COOKIE = "refresh_token"


@router.post("/register", response_model=StandardResponse[UserOut], status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user. Returns 409 on duplicate email, 422 on policy violation."""
    user = register_user(payload, db)
    return ok(UserOut.model_validate(user), "Registration successful.")


@router.post("/login", response_model=StandardResponse[TokenResponse])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate and return a short-lived in-memory JWT access token.
    Sets a secure, httpOnly refresh cookie for silent session hydration."""
    user = login_user(payload, db)
    token_data = {"sub": str(user.id), "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    result = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )
    return ok(result, "Login successful.")


@router.post("/refresh", response_model=StandardResponse[TokenResponse])
def refresh_session(request: Request, response: Response, db: Session = Depends(get_db)):
    """Hydrates an in-memory access token from the httpOnly refresh cookie.
    Never exposes refresh tokens to JavaScript runtime or Web Storage."""
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh session found.",
        )

    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type.")
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_active != "Y":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive or not found.")

    token_data = {"sub": str(user.id), "role": user.role}
    new_access_token = create_access_token(token_data)

    result = TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )
    return ok(result, "Session refreshed.")


@router.post("/logout", response_model=StandardResponse[dict])
def logout(response: Response):
    """Deletes the httpOnly refresh cookie from the client browser."""
    response.delete_cookie(
        key=REFRESH_COOKIE,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )
    return ok({"logged_out": True}, "Successfully logged out.")
