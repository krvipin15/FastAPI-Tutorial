import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import User
from app.schema import TokenData

# Load environment variables from .env file
load_dotenv()

# JWT configuration values
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2 scheme used by FastAPI to extract the Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.

    The token payload is copied from the provided data and
    augmented with an expiration (`exp`) claim.

    Args:
        data (dict): Payload data to encode (e.g., {"user_id": user.id})

    Returns:
        str: Encoded JWT access token
    """
    to_encode: dict = data.copy()
    expire: datetime = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    credentials_exception: HTTPException,
) -> TokenData:
    """
    Verify and decode a JWT access token.

    Ensures the token is valid, not expired, and contains
    the required user identifier.

    Args:
        token (str): JWT token extracted from the Authorization header
        credentials_exception (HTTPException): Exception to raise on failure

    Returns:
        TokenData: Parsed token data containing the user identifier

    Raises:
        HTTPException: If token is invalid or missing required claims
    """
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int | None = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

        return TokenData(username=user_id)

    except InvalidTokenError:
        raise credentials_exception


def get_current_active_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieve the currently authenticated user.

    This function:
    - Validates the JWT access token
    - Extracts the user ID
    - Fetches the corresponding user from the database

    Args:
        token (str): JWT token from the Authorization header
        db (Session): SQLAlchemy database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: If authentication fails or user does not exist
    """
    credentials_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data: TokenData = verify_access_token(token, credentials_exception)

    user: User | None = db.query(User).filter(User.id == token_data.username).first()

    if user is None:
        raise credentials_exception

    return user
