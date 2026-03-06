import uuid
from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import Uuid as UuidType

from .base import Base


def _uuid_column() -> Mapped[uuid.UUID]:
    return mapped_column(
        UuidType(),
        primary_key=True,
        default=uuid.uuid4,
    )


class Hotel(Base):
    __tablename__ = "hotels"

    id: Mapped[uuid.UUID] = _uuid_column()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="GBP")

    users: Mapped[list["User"]] = relationship("User", back_populates="hotel")
    integrations: Mapped[list["Integration"]] = relationship(
        "Integration", back_populates="hotel"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = _uuid_column()
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="owner")

    hotel_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(), ForeignKey("hotels.id"), nullable=False
    )
    hotel: Mapped[Hotel] = relationship("Hotel", back_populates="users")


class Integration(Base):
    __tablename__ = "integrations"

    id: Mapped[uuid.UUID] = _uuid_column()
    hotel_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(), ForeignKey("hotels.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="disconnected")
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    hotel: Mapped[Hotel] = relationship("Hotel", back_populates="integrations")
    credentials: Mapped[list["IntegrationCredential"]] = relationship(
        "IntegrationCredential", back_populates="integration"
    )

    __table_args__ = (
        UniqueConstraint("hotel_id", "type", name="uq_integration_hotel_type"),
    )


class IntegrationCredential(Base):
    __tablename__ = "integration_credentials"

    id: Mapped[uuid.UUID] = _uuid_column()
    integration_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(), ForeignKey("integrations.id"), nullable=False
    )
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    integration: Mapped[Integration] = relationship(
        "Integration", back_populates="credentials"
    )


class RevenueDailyMetric(Base):
    __tablename__ = "metrics_revenue_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(), ForeignKey("hotels.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    room_revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    other_revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="xero")


class OccupancyDailyMetric(Base):
    __tablename__ = "metrics_occupancy_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(), ForeignKey("hotels.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    rooms_available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rooms_sold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    occupancy_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hotel_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(), ForeignKey("hotels.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="info")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

