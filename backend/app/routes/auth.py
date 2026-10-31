"""Auth routes — register and login."""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import create_access_token, create_refresh_token
from backend.app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from backend.app.schemas.common import StandardResponse, ok
from backend.app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])

REFRESH_COOKIE = "refresh_token"


@router.post("/register", response_model=StandardResponse[UserOut], status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user. Returns 409 on duplicate email, 422 on policy violation."""
    user = register_user(payload, db)
    return ok(UserOut.model_validate(user), "Registration successful.")


@router.post("/login", response_model=StandardResponse[TokenResponse])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate and return a short-lived JWT access token.
    Also sets an httpOnly refresh token cookie."""
    user = login_user(payload, db)
    token_data = {"sub": str(user.id), "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    result = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )
    return ok(result, "Login successful.")
