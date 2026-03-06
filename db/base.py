from collections.abc import Generator
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from llm.config import DATABASE_URL


Base = declarative_base()


def _create_engine():
    # DATABASE_URL comes from environment via llm.config.
    # Default to a local SQLite file for development if not set.
    url = DATABASE_URL or os.getenv("DATABASE_URL", "sqlite:///./stayintel.db")
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, connect_args=connect_args)


engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

