"""
Initialize database: create tables and optionally seed demo data.
Called on app startup to ensure schema exists.
"""
import uuid

from db.base import Base, engine
from db import models  # noqa: F401 - register models with Base


# Fixed UUID for demo hotel so frontend can reference it consistently
DEMO_HOTEL_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


def init_db() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def seed_demo_data() -> None:
    """Insert demo hotel and user for showcase. Idempotent."""
    from sqlalchemy.orm import Session
    from db.base import SessionLocal
    from db.models import Hotel, User

    db = SessionLocal()
    try:
        hotel = db.query(Hotel).filter(Hotel.id == DEMO_HOTEL_ID).first()
        if not hotel:
            hotel = Hotel(
                id=DEMO_HOTEL_ID,
                name="The Grand Meridian",
                timezone="Europe/London",
                currency="GBP",
            )
            db.add(hotel)
            db.commit()
            db.refresh(hotel)

        user = db.query(User).filter(User.id == DEMO_USER_ID).first()
        if not user:
            user = User(
                id=DEMO_USER_ID,
                email="demo@stayintel.example",
                hashed_password=None,
                role="owner",
                hotel_id=DEMO_HOTEL_ID,
            )
            db.add(user)
            db.commit()
    finally:
        db.close()
