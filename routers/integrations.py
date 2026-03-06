"""
Integrations API - GET /integrations, POST /integrations/xero/connect
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.base import get_session
from db.init_db import DEMO_HOTEL_ID
from db.models import Integration

router = APIRouter(prefix="/integrations", tags=["integrations"])


def _resolve_hotel_id(x_hotel_id: Optional[str]) -> uuid.UUID:
    """Resolve hotel ID from header or default to demo."""
    if x_hotel_id and x_hotel_id != "hotel_001":
        try:
            return uuid.UUID(x_hotel_id)
        except ValueError:
            pass
    return DEMO_HOTEL_ID


@router.get("", response_model=list[IntegrationDisplay])
def list_integrations(
    x_hotel_id: Optional[str] = Header(None, alias="X-Hotel-Id"),
    db: Session = Depends(get_session),
):
    """
    List integrations for the hotel with display info.
    Frontend can sync store (e.g. xeroConnected) from this.
    """
    hotel_id = _resolve_hotel_id(x_hotel_id)
    integrations = db.query(Integration).filter(Integration.hotel_id == hotel_id).all()
    result = []
    for i in integrations:
        org_name = None
        if i.type == "xero" and i.config and isinstance(i.config, dict):
            org_name = i.config.get("organisation_name")
        if i.type == "xero" and not org_name:
            org_name = "The Grand Meridian Ltd"
        result.append(
            IntegrationDisplay(
                type=i.type,
                status=i.status,
                organisation_name=org_name,
                last_sync_at=i.last_sync_at,
            )
        )
    return result


class IntegrationDisplay(BaseModel):
    """Integration with display info for frontend."""
    type: str
    status: str
    organisation_name: Optional[str] = None
    last_sync_at: Optional[datetime] = None


class XeroConnectRequest(BaseModel):
    code: Optional[str] = None


class XeroConnectResponse(BaseModel):
    success: bool
    organisation_name: Optional[str] = None
    error: Optional[str] = None


@router.post("/xero/connect", response_model=XeroConnectResponse)
def connect_xero(
    body: XeroConnectRequest = XeroConnectRequest(),
    x_hotel_id: Optional[str] = Header(None, alias="X-Hotel-Id"),
    db: Session = Depends(get_session),
):
    """
    Simulate Xero OAuth connect. For showcase: creates/updates Integration row and returns success.
    Real OAuth flow would exchange code for tokens.
    """
    hotel_id = _resolve_hotel_id(x_hotel_id)
    org_name = "The Grand Meridian Ltd"

    try:
        integration = (
            db.query(Integration)
            .filter(
                Integration.hotel_id == hotel_id,
                Integration.type == "xero",
            )
            .first()
        )
        if integration:
            integration.status = "connected"
            integration.last_sync_at = datetime.now(timezone.utc)
            integration.config = {**(integration.config or {}), "organisation_name": org_name}
        else:
            integration = Integration(
                hotel_id=hotel_id,
                type="xero",
                status="connected",
                last_sync_at=datetime.now(timezone.utc),
                config={"organisation_name": org_name},
            )
            db.add(integration)
        db.commit()
        return XeroConnectResponse(success=True, organisation_name=org_name)
    except Exception as e:
        db.rollback()
        return XeroConnectResponse(success=False, error=str(e))
