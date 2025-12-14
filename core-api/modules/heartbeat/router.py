"""
DeckBrain Core API - Heartbeat endpoints.

Handles periodic status updates from connectors.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from core.db import get_db
from core.models import Device, Heartbeat
from core.auth import get_authenticated_device


logger = logging.getLogger(__name__)
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
    device: Device = Depends(get_authenticated_device),
    db: Session = Depends(get_db)
):
    """
    Receive heartbeat from connector.
    
    Stores heartbeat data for an authenticated device.
    
    Headers:
    - X-Device-ID: Required. Unique device identifier.
    - X-API-Key: Required. API key for authentication.
    - X-Plotter-Type: Optional. Plotter type (olex, maxsea, etc.) - only used for auto-registration in dev mode.
    
    TODO:
    - Add rate limiting
    - Add more detailed response with sync recommendations
    - Hide database initialization errors in production (return generic 500)
    """
    try:
        # Device is already authenticated by dependency
        # last_seen_at is already updated by auth dependency
        
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
        
        logger.info(f"Heartbeat received from device {device.device_id}")
        
        return HeartbeatResponse(
            status="ok",
            device_id=device.device_id,
            received_at=heartbeat.received_at,
        )
    except OperationalError as e:
        # Check if error is about missing tables
        error_msg = str(e).lower()
        if "no such table" in error_msg or "does not exist" in error_msg:
            logger.error("Database not initialized - missing tables")
            raise HTTPException(
                status_code=500,
                detail="Database not initialized. Please run migrations: alembic upgrade head"
            )
        # Re-raise other operational errors
        logger.error(f"OperationalError in heartbeat: {e}")
        raise

