from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database import Base


class Post(Base):
    """
    SQLAlchemy model representing a social media post.

    Each post belongs to a user and contains textual content
    along with publication metadata.
    """

    __tablename__ = "posts"

    # Primary key uniquely identifying each post
    id: Column[int] = Column(
        Integer,
        primary_key=True,
        nullable=False,
        index=True,
    )

    # Foreign key linking the post to its owner
    owner_id: Column[int] = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Human-readable title of the post
    title: Column[str] = Column(
        String,
        nullable=False,
    )

    # Main body/content of the post
    content: Column[str] = Column(
        String,
        nullable=False,
    )

    # Indicates whether the post is publicly visible
    published: Column[bool] = Column(
        Boolean,
        server_default="true",
        nullable=False,
    )

    # Timestamp indicating when the post was created
    created_at: Column[datetime] = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    owner = relationship("User")


class User(Base):
    """
    SQLAlchemy model representing an application user.

    Stores authentication credentials and basic identity data.
    """

    __tablename__ = "users"

    # Primary key uniquely identifying each user
    id: Column[int] = Column(
        Integer,
        primary_key=True,
        nullable=False,
        index=True,
    )

    # User's email address
    email: Column[str] = Column(
        String,
        nullable=False,
        unique=True,
    )

    # Hashed password
    password: Column[str] = Column(
        String,
        nullable=False,
    )

    # Timestamp indicating when the user account was created
    created_at: Column[datetime] = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Vote(Base):
    """
    SQLAlchemy model representing vote on a post.

    Each post is either liked or not liked by the user.
    """
    __tablename__ = "votes"

    # Foreign key linking the post to its owner
    post_id: Column[int] = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Foreign key linking the post to its owner
    owner_id: Column[int] = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
