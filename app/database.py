import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Load environment variables
load_dotenv()

# Access variable values
DATABASE: str = os.getenv("DATABASE", "")
USER: str = os.getenv("USER", "")
PASSWORD: str = os.getenv("PASSWORD", "")
HOST: str = os.getenv("HOST", "localhost")
PORT: str = os.getenv("PORT", "5432")

# Database connection
DATABASE_URL: str = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# Create the SQLAlchemy engine responsible for database connections
engine: Engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session factory for creating database sessions
# - autoflush=False: avoids automatic flushes before queries
# - autocommit=False: enforces explicit transaction management
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# Base class for all SQLAlchemy ORM models
class Base(DeclarativeBase):
    pass
