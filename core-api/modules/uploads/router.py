"""
DeckBrain Core API - Upload endpoints.

Handles raw file uploads from connectors with authentication.
"""

import os
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from pydantic import BaseModel

from core.db import get_db
from core.models import Device, FileRecord
from core.auth import get_authenticated_device
from core.config import settings
from modules.ingestion.service import ingest_file_safe


logger = logging.getLogger(__name__)
router = APIRouter()


class UploadResponse(BaseModel):
    """Response model for upload endpoint."""
    status: str
    file_record_id: int
    remote_path: str
    size_bytes: int
    sha256: str
    processing_status: str


def compute_sha256(file_path: Path) -> str:
    """
    Compute SHA256 hash of a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Hexadecimal SHA256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def ensure_storage_dir_exists(device_id: str) -> Path:
    """
    Ensure storage directory exists for a device.
    
    Creates directory structure: storage/devices/<device_id>/raw/<yyyy>/<mm>/<dd>/
    
    Args:
        device_id: Device identifier
        
    Returns:
        Path to storage directory for today
    """
    now = datetime.utcnow()
    storage_path = Path(settings.storage_path) / "devices" / device_id / "raw" / f"{now.year:04d}" / f"{now.month:02d}" / f"{now.day:02d}"
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


@router.post("/upload_file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: Optional[str] = Form("unknown"),
    source_format: Optional[str] = Form("unknown"),
    local_path: Optional[str] = Form(None),
    captured_at: Optional[str] = Form(None),
    device: Device = Depends(get_authenticated_device),
    db: Session = Depends(get_db)
):
    """
    Upload a raw plotter file to the Core API.
    
    This is a vendor-agnostic endpoint used by all connector types (Olex, MaxSea, etc.).
    The server determines the plotter type from the authenticated device.
    
    Headers (handled by auth dependency):
    - X-Device-ID: Required. Unique device identifier.
    - X-API-Key: Required. API key for authentication.
    - X-Plotter-Type: Optional. Only used for auto-registration in dev mode.
    
    Form Data (multipart/form-data):
    - file: Required. The file to upload (binary).
    - file_type: Optional. Logical type (track, soundings, marks, backup, unknown). Default: "unknown".
    - source_format: Optional. File format hint (olex_raw, maxsea_mf2, etc.). Default: "unknown".
    - local_path: Optional. Path on connector's disk (for reference).
    - captured_at: Optional. ISO datetime when file was created/captured.
    
    Returns:
        UploadResponse with file_record_id, remote_path, size_bytes, sha256, and processing_status.
        
    Raises:
        HTTPException 400: Missing file or validation error
        HTTPException 401: Authentication failed (handled by dependency)
        HTTPException 500: Server error (storage failure, database error)
    """
    try:
        # Validate file
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File has no filename"
            )
        
        logger.info(f"Receiving file upload from device {device.device_id}: {file.filename}")
        
        # Ensure storage directory exists
        storage_dir = ensure_storage_dir_exists(device.device_id)
        
        # Generate unique filename: <uuid>__<original_filename>
        file_uuid = str(uuid4())
        safe_filename = file.filename.replace("/", "_").replace("\\", "_")  # Sanitize
        unique_filename = f"{file_uuid}__{safe_filename}"
        file_path = storage_dir / unique_filename
        
        # Save file to disk
        try:
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            logger.info(f"Saved file to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Compute file metadata
        size_bytes = os.path.getsize(file_path)
        sha256_hash = compute_sha256(file_path)
        
        # Create relative path for storage (relative to storage root)
        relative_path = str(file_path.relative_to(Path(settings.storage_path)))
        
        # Create file record in database
        file_record = FileRecord(
            device_id=device.id,
            file_type=file_type or "unknown",
            source_format=source_format or "unknown",
            local_path=local_path,  # Path on connector's disk
            remote_path=relative_path,  # Path in Core API storage
            size_bytes=size_bytes,
            sha256=sha256_hash,
            processing_status="stored",  # File is now stored, awaiting processing
            received_at=datetime.utcnow()
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        logger.info(f"File record created: id={file_record.id}, device={device.device_id}, size={size_bytes}, sha256={sha256_hash[:8]}...")
        
        # Auto-trigger ingestion in development mode
        final_processing_status = file_record.processing_status
        if settings.app_env == "development":
            logger.info(f"[AUTO-INGEST] Triggering ingestion for file_record_id={file_record.id} (dev mode)")
            ingestion_result = ingest_file_safe(file_record.id, db)
            
            if ingestion_result["status"] == "success":
                logger.info(f"[AUTO-INGEST] Ingestion completed successfully for file_record_id={file_record.id}")
                logger.info(f"[AUTO-INGEST] Status: {ingestion_result.get('message', 'No message')}")
                # Refresh file_record to get updated processing_status
                db.refresh(file_record)
                final_processing_status = file_record.processing_status
            elif ingestion_result["status"] == "failed":
                logger.warning(f"[AUTO-INGEST] Ingestion failed (parser) for file_record_id={file_record.id}: {ingestion_result.get('message')}")
                db.refresh(file_record)
                final_processing_status = file_record.processing_status
            else:
                # Error cases (FileNotFoundError, NoParserError, etc.)
                logger.error(f"[AUTO-INGEST] Ingestion error for file_record_id={file_record.id}: {ingestion_result.get('error_type')} - {ingestion_result.get('message')}")
                db.refresh(file_record)
                final_processing_status = file_record.processing_status
        else:
            logger.debug(f"Auto-ingestion skipped (app_env={settings.app_env}, not 'development')")
        
        return UploadResponse(
            status="ok",
            file_record_id=file_record.id,
            remote_path=relative_path,
            size_bytes=size_bytes,
            sha256=sha256_hash,
            processing_status=final_processing_status
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (auth errors, validation errors)
        raise
    except OperationalError as e:
        # Database errors
        error_msg = str(e).lower()
        if "no such table" in error_msg or "does not exist" in error_msg:
            logger.error("Database not initialized - missing tables")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database not initialized. Please run migrations: alembic upgrade head"
            )
        logger.error(f"OperationalError in upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in upload_file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

