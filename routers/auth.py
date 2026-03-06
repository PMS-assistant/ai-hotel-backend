"""
Auth API - POST /auth/login, GET /auth/me
Simple auth for showcase; no real JWT.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from db.base import get_session
from db.init_db import DEMO_HOTEL_ID, DEMO_USER_ID, seed_demo_data
from db.models import Hotel, User

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    role: str = "owner"  # owner | manager | staff


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    hotelId: str


class LoginResponse(BaseModel):
    user: UserResponse
    token: Optional[str] = None


def _resolve_hotel_id(x_hotel_id: Optional[str]) -> uuid.UUID:
    if x_hotel_id and x_hotel_id != "hotel_001":
        try:
            return uuid.UUID(x_hotel_id)
        except ValueError:
            pass
    return DEMO_HOTEL_ID


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    db: Session = Depends(get_session),
):
    """
    Login with email and role. Creates or finds user; returns user + optional token.
    For showcase, ensures demo hotel/user exist.
    """
    seed_demo_data()

    # Validate role
    if body.role not in ("owner", "manager", "staff"):
        body.role = "owner"

    # Find or create user - use demo hotel for showcase
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        user = User(
            email=body.email,
            hashed_password=None,
            role=body.role,
            hotel_id=DEMO_HOTEL_ID,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update role for returning users so login can change role (e.g. owner -> manager)
        if user.role != body.role:
            user.role = body.role
            db.commit()
            db.refresh(user)

    return LoginResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            hotelId=str(user.hotel_id),
        ),
        token=f"demo_{user.id}",
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_hotel_id: Optional[str] = Header(None, alias="X-Hotel-Id"),
    db: Session = Depends(get_session),
):
    """
    Return current user from X-User-Id / X-Hotel-Id headers.
    For showcase: if X-User-Id looks like user_123 (frontend format), use demo user.
    """
    seed_demo_data()

    # Frontend may send "user_123" or UUID
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = None
    if x_user_id.startswith("user_"):
        # Frontend format before API login - return demo user
        hotel_id = _resolve_hotel_id(x_hotel_id)
        user = db.query(User).filter(User.hotel_id == hotel_id).first()
        if not user:
            user = db.query(User).filter(User.id == DEMO_USER_ID).first()
    else:
        try:
            uid = uuid.UUID(x_user_id)
            user = db.query(User).filter(User.id == uid).first()
        except ValueError:
            pass

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        hotelId=str(user.hotel_id),
    )
