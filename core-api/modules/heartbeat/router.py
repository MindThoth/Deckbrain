"""
DeckBrain Core API - Heartbeat endpoints.

Handles periodic status updates from connectors.
"""

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from core.db import get_db
from core.models import Device, Heartbeat


router = APIRouter()


class HeartbeatRequest(BaseModel):
    """Request model for heartbeat endpoint."""
    queue_size: Optional[int] = None
    last_upload_ok: Optional[bool] = None
    connector_version: Optional[str] = None


class HeartbeatResponse(BaseModel):
    """Response model for heartbeat endpoint."""
    status: str
    device_id: str
    received_at: datetime


@router.post("/heartbeat", response_model=HeartbeatResponse)
def receive_heartbeat(
    request: HeartbeatRequest,
    x_device_id: str = Header(..., alias="X-Device-ID"),
    x_plotter_type: Optional[str] = Header(None, alias="X-Plotter-Type"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Receive heartbeat from connector.
    
    Creates or updates device record and stores heartbeat data.
    
    Headers:
    - X-Device-ID: Required. Unique device identifier.
    - X-Plotter-Type: Optional. Plotter type (olex, maxsea, etc.)
    - X-API-Key: Optional. API key for authentication (not enforced yet).
    
    TODO:
    - Implement API key validation
    - Add rate limiting
    - Add more detailed response with sync recommendations
    """
    # Find or create device
    device = db.query(Device).filter(Device.device_id == x_device_id).first()
    
    if not device:
        # Create new device if not exists
        plotter_type = x_plotter_type if x_plotter_type else "other"
        device = Device(
            device_id=x_device_id,
            plotter_type=plotter_type,
            last_seen_at=datetime.utcnow()
        )
        db.add(device)
        db.flush()  # Get device.id before creating heartbeat
    else:
        # Update last_seen_at
        device.last_seen_at = datetime.utcnow()
    
    # Create heartbeat record
    heartbeat = Heartbeat(
        device_id=device.id,
        queue_size=request.queue_size,
        last_upload_ok=request.last_upload_ok,
        connector_version=request.connector_version,
    )
    db.add(heartbeat)
    
    # Commit transaction
    db.commit()
    db.refresh(heartbeat)
    
    return HeartbeatResponse(
        status="ok",
        device_id=x_device_id,
        received_at=heartbeat.received_at,
    )

