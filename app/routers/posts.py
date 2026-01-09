from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Post, User, Vote
from app.oauth2 import get_current_active_user
from app.schema import PostCreate, PostJoin, PostSchema

# Router responsible for post-related operations
router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post(
    "/",
    response_model=PostSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    post: PostCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Post:
    """
    Create a new post owned by the currently authenticated user.

    Args:
        post (PostCreate): Validated post creation payload.
        db (Session): SQLAlchemy database session.
        current_user (User): Authenticated user.

    Returns:
        Post: Newly created post.
    """
    new_post: Post = Post(
        **post.model_dump(),
        owner_id=current_user.id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/", response_model=list[PostJoin])
def get_posts(
    db: Annotated[Session, Depends(get_db)],
    limit: int = 10,
    skip: int = 0,
    search: str = "",
) -> list[PostJoin]:
    """
    Retrieve all posts.

    Args:
        db (Session): database session.

    Returns:
        list[PostJoin]: List of posts with vote counts.
    """
    posts: tuple = (
        db.query(Post, func.count(Vote.post_id).label("votes"))
        .join(Vote, Vote.post_id == Post.id, isouter=True)
        .group_by(Post.id)
        .filter(Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    # Convert the query results to PostJoin objects
    result: list = []
    for post, votes_count in posts:
        post_join: PostJoin = PostJoin(post=post, votes=votes_count)
        result.append(post_join)

    return result


@router.get("/{id}", response_model=PostJoin)
def get_post(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> PostJoin:
    """
    Retrieve a single post by ID.

    Args:
        id (int): Post ID.
        db (Session): SQLAlchemy database session.

    Returns:
        Post: Requested post.

    Raises:
        HTTPException: If the post does not exist.
    """
    post: tuple | None = (
        db.query(Post, func.count(Vote.post_id).label("votes"))
        .join(Vote, Vote.post_id == Post.id, isouter=True)
        .group_by(Post.id)
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} not found",
        )

    # Convert the query results to PostJoin objects
    post_data, votes_count = post
    return PostJoin(post=post_data, votes=votes_count)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    """
    Delete a post owned by the current user.

    Args:
        id (int): Post ID.
        db (Session): SQLAlchemy database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: If post does not exist or user is not the owner.
    """
    post: Post | None = db.query(Post).filter(Post.id == id).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} not found",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    db.delete(post)
    db.commit()

    return None


@router.put("/{id}", response_model=PostSchema)
def update_post(
    id: int,
    post: PostCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Post:
    """
    Update an existing post owned by the current user.

    Args:
        id (int): Post ID.
        post (PostCreate): Updated post data.
        db (Session): SQLAlchemy database session.
        current_user (User): Authenticated user.

    Returns:
        Post: Updated post.

    Raises:
        HTTPException: If post does not exist or user is not the owner.
    """
    db_post: Post | None = db.query(Post).filter(Post.id == id).first()

    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} not found",
        )

    if db_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    for key, value in post.model_dump().items():
        setattr(db_post, key, value)

    db.commit()
    db.refresh(db_post)

    return db_post
