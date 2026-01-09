from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import User
from app.oauth2 import create_access_token
from app.schema import Token
from app.utils import verify_password

# Router responsible for authentication endpoints
router = APIRouter(
    tags=["Authentication"],
)


@router.post("/login", response_model=Token)
def login(
    user_credentials: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: Session = Depends(get_db),
) -> Token:
    """
    Authenticate a user and issue a JWT access token.

    This endpoint:
    - Validates user credentials
    - Verifies the password
    - Issues a signed JWT access token

    Args:
        user_credentials (OAuth2PasswordRequestForm): OAuth2 login form data.
        db (Session): SQLAlchemy database session.

    Returns:
        Token: Access token and token type.

    Raises:
        HTTPException: If authentication fails.
    """
    # Retrieve user by email (OAuth2 uses "username" field)
    user: User | None = db.query(User).filter(User.email == user_credentials.username).first()

    # Do not reveal whether the user exists (security best practice)
    if user is None or not verify_password(
        user_credentials.password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT access token
    access_token: str = create_access_token(data={"user_id": user.id})

    return Token(
        access_token=access_token,
        token_type="bearer",
    )
