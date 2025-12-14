"""
DeckBrain Core API - Authentication utilities.

Handles device authentication for connector endpoints.
"""

import hashlib
import hmac
import logging
from datetime import datetime
from typing import Optional

from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session

from core.db import get_db
from core.models import Device
from core.config import settings


logger = logging.getLogger(__name__)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage using SHA256.
    
    API keys are typically long, random strings (unlike passwords),
    so SHA256 is appropriate for hashing them.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        Hexadecimal SHA256 hash of the API key
    """
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against a hashed version using constant-time comparison.
    
    Args:
        plain_key: Plain text API key from request
        hashed_key: Hashed API key from database
        
    Returns:
        True if key matches, False otherwise
    """
    computed_hash = hash_api_key(plain_key)
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(computed_hash, hashed_key)


def get_authenticated_device(
    x_device_id: str = Header(..., alias="X-Device-ID"),
    x_api_key: str = Header(..., alias="X-API-Key"),
    x_plotter_type: Optional[str] = Header(None, alias="X-Plotter-Type"),
    db: Session = Depends(get_db)
) -> Device:
    """
    FastAPI dependency for authenticating connector requests.
    
    Validates device credentials and returns the authenticated device.
    
    Headers:
        X-Device-ID: Required. Unique device identifier.
        X-API-Key: Required. API key for authentication.
        X-Plotter-Type: Optional. Plotter type (olex, maxsea, etc.)
    
    Returns:
        Authenticated Device object
        
    Raises:
        HTTPException 400: Missing required headers
        HTTPException 401: Invalid credentials or device not registered
    """
    # Validate required headers
    if not x_device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required header: X-Device-ID"
        )
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required header: X-API-Key"
        )
    
    # Look up device by device_id
    device = db.query(Device).filter(Device.device_id == x_device_id).first()
    
    if device:
        # Device exists - validate API key
        if not device.api_key_hash:
            # Device exists but has no API key set (should not happen in normal flow)
            logger.warning(f"Device {x_device_id} exists but has no API key hash. Rejecting request.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Device authentication not configured. Please contact support."
            )
        
        # Verify API key
        if not verify_api_key(x_api_key, device.api_key_hash):
            logger.warning(f"Invalid API key for device {x_device_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key for device"
            )
        
        # Update last_seen_at
        device.last_seen_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Device {x_device_id} authenticated successfully")
        return device
    
    else:
        # Device does not exist
        if settings.app_env == "development":
            # In development mode, auto-create device with provided credentials
            logger.info(f"Auto-creating device {x_device_id} in development mode")
            
            plotter_type = x_plotter_type if x_plotter_type else "other"
            
            new_device = Device(
                device_id=x_device_id,
                plotter_type=plotter_type,
                api_key_hash=hash_api_key(x_api_key),
                last_seen_at=datetime.utcnow()
            )
            
            db.add(new_device)
            db.commit()
            db.refresh(new_device)
            
            logger.info(f"Created new device {x_device_id} with plotter_type={plotter_type}")
            return new_device
        
        else:
            # In production mode, reject unregistered devices
            logger.warning(f"Device {x_device_id} not registered (production mode)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Device not registered. Please register your device first."
            )

