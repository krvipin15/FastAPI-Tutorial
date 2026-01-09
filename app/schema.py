from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    The password is expected to be plain text and will be
    hashed before persisting to the database.
    """

    email: EmailStr
    password: str


class UserSchema(BaseModel):
    """
    Schema representing a user returned by the API.

    Sensitive fields such as passwords are intentionally excluded.
    """

    id: int
    email: EmailStr
    created_at: datetime

    # Enable compatibility with ORM objects (e.g., SQLAlchemy models)
    model_config: dict = {"from_attributes": True}


class UserLogin(BaseModel):
    """
    Schema for user authentication (login).

    Used to validate login credentials.
    """

    email: EmailStr
    password: str


class PostCreate(BaseModel):
    """
    Schema for creating a new post.

    Used as the request body when a client creates a post.
    """

    title: str
    content: str
    published: bool = True


class PostSchema(BaseModel):
    """
    Schema representing a post as returned by the API.

    Includes database-generated fields such as ID and timestamps.
    """

    id: int
    owner_id: int
    owner: UserSchema
    title: str
    content: str
    published: bool
    created_at: datetime

    # Enable compatibility with ORM objects (e.g., SQLAlchemy models)
    model_config: dict = {"from_attributes": True}


class PostJoin(BaseModel):
    """
    Schema for representing votes with other post data.

    Completes information on post.
    """
    post: PostSchema
    votes: int

    # Enable compatibility with ORM objects (e.g., SQLAlchemy models)
    model_config: dict = {"from_attributes": True}


class VoteSchema(BaseModel):
    """
    Schema for creating a new vote

    vote can be 0 (not liked) or 1 (liked).
    """
    post_id: int
    dir: Literal[0, 1]


class VoteResponse(BaseModel):
    """
    Schema for representing votes

    Returns ids of posts with user id who voted on them.
    """
    post_id: int
    owner_id: int

    # Enable compatibility with ORM objects (e.g., SQLAlchemy models)
    model_config: dict = {"from_attributes": True}


class Token(BaseModel):
    """
    Schema for an authentication token response.

    Returned after successful login.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for data extracted from a JWT token.

    Used internally for authentication/authorization.
    """

    username: int | None = None
