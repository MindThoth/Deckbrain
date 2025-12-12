"""
DeckBrain Core API - Device management endpoints.

Handles device registration, listing, and status queries.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from core.db import get_db
from core.models import Device as DeviceModel


router = APIRouter()


class DeviceResponse(BaseModel):
    """Device model for API responses."""
    device_id: str
    name: Optional[str] = None
    plotter_type: str
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Response model for device listing."""
    devices: List[DeviceResponse]
    total: int


@router.get("/devices", response_model=DeviceListResponse)
def list_devices(db: Session = Depends(get_db)):
    """
    List all registered devices.
    
    Returns list of devices from the database.
    
    TODO:
    - Add pagination support
    - Add filtering by plotter_type, status, etc.
    - Implement authentication/authorization
    """
    devices = db.query(DeviceModel).all()
    return DeviceListResponse(
        devices=[DeviceResponse.model_validate(device) for device in devices],
        total=len(devices),
    )


@router.get("/devices/{device_id}", response_model=DeviceResponse)
def get_device(device_id: str, db: Session = Depends(get_db)):
    """
    Get details for a specific device.
    
    Returns device by device_id or 404 if not found.
    
    TODO:
    - Add authentication/authorization
    - Include additional device metadata (heartbeat stats, file counts)
    """
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return DeviceResponse.model_validate(device)

