from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session.

    This function is typically used with dependency injection frameworks
    (e.g., FastAPI) to ensure that a database session is:
    - Created when a request starts
    - Properly closed after the request finishes

    Yields:
        Session: An active SQLAlchemy database session.
    """
    # Create a new database session
    db: Session = SessionLocal()
    try:
        # Provide the session to the caller
        yield db
    finally:
        # Always close the session to release connections
        db.close()
