"""
Dashboard API - GET /dashboard/summary
Returns KPIs, alerts, forecast, pickup matching frontend DashboardData shape.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from db.base import get_session
from db.init_db import DEMO_HOTEL_ID
from db.schemas import (
    AlertData,
    DashboardSummaryResponse,
    ForecastPoint,
    KPIData,
    PickupPoint,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Mock data matching frontend mockData.ts - used when DB has no metrics
MOCK_KPIS = KPIData(
    occupancyToday=71.3,
    occupancyTrend=-2.8,
    adrToday=142.5,
    adrTrend=4.2,
    revpar=101.6,
    revparTrend=-1.4,
    roomsAvailable=27,
    totalRooms=94,
    cancellationRate=8.2,
    cancellationRateTrend=4.3,
)

MOCK_ALERTS = [
    AlertData(
        id="alert_1",
        title="Cancellations running 2× baseline",
        description="OTA cancellations elevated at 8.2% vs 3.9% baseline. 14 room nights lost this week representing ~£1,995 in unrealised revenue.",
        severity="warning",
        timestamp="2026-02-27T08:15:00Z",
        category="Revenue",
    ),
    AlertData(
        id="alert_2",
        title="Weekend demand unusually high",
        description="Saturday tracking at 94% occupancy with 4 days remaining. Current BAR of £149 may be suppressed — yield review recommended.",
        severity="info",
        timestamp="2026-02-27T07:30:00Z",
        category="Demand",
    ),
    AlertData(
        id="alert_3",
        title="Check-in congestion expected 14:00–16:00",
        description="23 arrivals confirmed in a 2-hour window today. Consider pre-arrival guest communications to stagger check-ins.",
        severity="warning",
        timestamp="2026-02-27T06:00:00Z",
        category="Operations",
    ),
    AlertData(
        id="alert_4",
        title="3 VIP arrivals without pre-authorisation",
        description="Rooms 204, 312, 418 require card pre-authorisation before arrival. Contact front desk to process before 12:00.",
        severity="critical",
        timestamp="2026-02-27T09:00:00Z",
        category="Operations",
    ),
]

MOCK_FORECAST = [
    ForecastPoint(date="Fri 28", occupancy=68, revpar=87, adr=128),
    ForecastPoint(date="Sat 1 Mar", occupancy=94, revpar=149, adr=158),
    ForecastPoint(date="Sun 2 Mar", occupancy=89, revpar=126, adr=142),
    ForecastPoint(date="Mon 3", occupancy=61, revpar=68, adr=112),
    ForecastPoint(date="Tue 4", occupancy=58, revpar=63, adr=108),
    ForecastPoint(date="Wed 5", occupancy=64, revpar=76, adr=118),
    ForecastPoint(date="Thu 6", occupancy=71, revpar=93, adr=131),
]

MOCK_PICKUP = [
    PickupPoint(day="Mon", thisWeek=8, lastWeek=5),
    PickupPoint(day="Tue", thisWeek=12, lastWeek=9),
    PickupPoint(day="Wed", thisWeek=7, lastWeek=6),
    PickupPoint(day="Thu", thisWeek=11, lastWeek=8),
    PickupPoint(day="Fri", thisWeek=9, lastWeek=11),
    PickupPoint(day="Sat", thisWeek=14, lastWeek=10),
    PickupPoint(day="Sun", thisWeek=4, lastWeek=7),
]


def _resolve_hotel_id(
    hotel_id_param: Optional[str],
    x_hotel_id: Optional[str],
) -> uuid.UUID:
    """Resolve hotel ID from query param, header, or default to demo."""
    if hotel_id_param:
        try:
            return uuid.UUID(hotel_id_param)
        except ValueError:
            pass
    if x_hotel_id and x_hotel_id != "hotel_001":
        try:
            return uuid.UUID(x_hotel_id)
        except ValueError:
            pass
    return DEMO_HOTEL_ID


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    hotel_id: Optional[str] = None,
    x_hotel_id: Optional[str] = Header(None, alias="X-Hotel-Id"),
    db: Session = Depends(get_session),
):
    """
    Get dashboard summary: KPIs, alerts, forecast, pickup.
    Uses mock data for showcase; can later query metrics_revenue_daily, metrics_occupancy_daily, alerts from DB.
    """
    # For now always return mock data
    return DashboardSummaryResponse(
        kpis=MOCK_KPIS,
        alerts=MOCK_ALERTS,
        forecast=MOCK_FORECAST,
        pickup=MOCK_PICKUP,
    )
