from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import User
from app.schema import UserCreate, UserSchema
from app.utils import hash_password

# Router responsible for user-related operations
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    """
    Create a new user account.

    This endpoint:
    - Hashes the user's password
    - Persists the user to the database
    - Returns the created user (excluding password)

    Args:
        user (UserCreate): Validated user creation payload.
        db (Session): SQLAlchemy database session.

    Returns:
        User: Newly created user instance.
    """
    # Hash the plain-text password before storing it
    hashed_password: str = hash_password(user.password)

    # Create a new User ORM instance
    new_user: User = User(
        **user.model_dump(exclude={"password"}),
        password=hashed_password,
    )

    # Persist user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get(
    "/{id}",
    response_model=UserSchema,
)
def get_user(
    id: int,
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieve a user by ID.

    Args:
        id (int): Unique identifier of the user.
        db (Session): SQLAlchemy database session.

    Returns:
        User: User matching the given ID.

    Raises:
        HTTPException: If the user does not exist.
    """
    user: User | None = db.query(User).filter(User.id == id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id {id} not found",
        )

    return user
