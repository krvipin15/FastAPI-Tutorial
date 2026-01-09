from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import User, Vote
from app.oauth2 import get_current_active_user
from app.schema import VoteResponse, VoteSchema

# Router responsible for vote-related operations
router = APIRouter(
    prefix="/votes",
    tags=["Votes"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=VoteResponse,
)
def vote(
    vote: VoteSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Vote | Response:
    """
    Create or delete a vote on a post.

    A vote is idempotent:
    - dir == 1 → add vote
    - dir == 0 → remove vote

    Args:
        vote (VoteCreate): Vote payload (post_id + direction).
        db (Session): SQLAlchemy database session.
        current_user (User): Authenticated user.

    Returns:
        Vote: Created vote.

    Raises:
        HTTPException: On invalid or conflicting operations.
    """
    # Check if the user has already voted on the post
    vote_query = db.query(Vote).filter(
        Vote.post_id == vote.post_id,
        Vote.owner_id == current_user.id,
    )
    existing_vote: Vote | None = vote_query.first()

    # Add vote
    if vote.dir == 1:
        if existing_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"user {current_user.id} has already voted on post {vote.post_id}",
            )
        new_vote: Vote = Vote(
            post_id=vote.post_id,
            owner_id=current_user.id,
        )

        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)

        return new_vote

    # Remove vote
    if vote.dir == 0:
        if not existing_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote does not exist",
            )

        vote_query.delete(synchronize_session=False)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # Invalid direction value
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid vote direction",
    )
