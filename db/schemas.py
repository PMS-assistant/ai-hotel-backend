from datetime import date, datetime
import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr


class HotelBase(BaseModel):
    name: str
    timezone: str = "UTC"
    currency: str = "GBP"


class HotelOut(HotelBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    role: str = "owner"


class UserOut(UserBase):
    id: uuid.UUID
    hotel_id: uuid.UUID

    class Config:
        from_attributes = True


class IntegrationOut(BaseModel):
    id: uuid.UUID
    hotel_id: uuid.UUID
    type: str
    status: str
    last_sync_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    id: int
    hotel_id: uuid.UUID
    created_at: datetime
    type: str
    severity: str
    title: str
    description: str

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    hotel_id: uuid.UUID
    from_date: date
    to_date: date
    total_revenue: float
    average_occupancy_pct: float
    alerts: list[AlertOut]


# Dashboard API response - matches frontend DashboardData shape
class KPIData(BaseModel):
    occupancyToday: float
    occupancyTrend: float
    adrToday: float
    adrTrend: float
    revpar: float
    revparTrend: float
    roomsAvailable: int
    totalRooms: int
    cancellationRate: float
    cancellationRateTrend: float


class AlertData(BaseModel):
    id: str
    title: str
    description: str
    severity: str  # info | warning | critical
    timestamp: str
    category: str


class ForecastPoint(BaseModel):
    date: str
    occupancy: float
    revpar: float
    adr: float


class PickupPoint(BaseModel):
    day: str
    thisWeek: int
    lastWeek: int


class DashboardSummaryResponse(BaseModel):
    kpis: KPIData
    alerts: list[AlertData]
    forecast: list[ForecastPoint]
    pickup: list[PickupPoint]

