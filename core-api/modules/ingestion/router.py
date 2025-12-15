"""
DeckBrain Core API - Ingestion endpoints.

Provides manual ingestion trigger endpoints for development and debugging.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.db import get_db
from core.models import FileRecord
from core.auth import get_authenticated_device
from .service import ingest_file_safe
from .registry import get_registry

logger = logging.getLogger(__name__)
router = APIRouter()


class IngestResponse(BaseModel):
    """Response model for ingestion endpoint."""
    status: str
    file_record_id: int
    message: str
    parsed_entities_count: Optional[int] = None
    metadata: Optional[dict] = None
    error_type: Optional[str] = None


class RegistryResponse(BaseModel):
    """Response model for parser registry listing."""
    parsers: dict


@router.post("/ingest/{file_record_id}", response_model=IngestResponse)
async def trigger_ingestion(
    file_record_id: int,
    db: Session = Depends(get_db)
):
    """
    Manually trigger ingestion for a specific file_record.
    
    **DEV/DEBUG ENDPOINT**: This endpoint is intended for development and debugging.
    In production, ingestion will be triggered automatically after upload.
    
    This endpoint does NOT require authentication to simplify dev testing.
    In production, this should be protected or removed.
    
    Args:
        file_record_id: ID of the FileRecord to ingest
        db: Database session
        
    Returns:
        IngestResponse with ingestion status and results
        
    Raises:
        HTTPException 404: If file_record not found
        HTTPException 400: If file_record has invalid status
        HTTPException 500: For other ingestion errors
    """
    logger.info(f"Manual ingestion triggered for file_record_id={file_record_id}")
    
    # Call ingestion service
    result = ingest_file_safe(file_record_id, db)
    
    # Map service result to HTTP response
    if result["status"] == "success":
        return IngestResponse(
            status="ok",
            file_record_id=file_record_id,
            message=result["message"],
            parsed_entities_count=result.get("parsed_entities_count"),
            metadata=result.get("metadata")
        )
    elif result["status"] == "failed":
        return IngestResponse(
            status="failed",
            file_record_id=file_record_id,
            message=result["message"],
            parsed_entities_count=result.get("parsed_entities_count"),
            metadata=result.get("metadata")
        )
    else:  # error
        error_type = result.get("error_type")
        
        # Map error types to HTTP status codes
        if error_type == "FileNotFoundError":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        elif error_type == "InvalidStatusError":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )


@router.get("/ingest/parsers", response_model=RegistryResponse)
async def list_parsers():
    """
    List all registered parsers.
    
    **DEV/DEBUG ENDPOINT**: This endpoint shows which parsers are available
    and what source_formats they handle.
    
    Returns:
        RegistryResponse with dict mapping source_format to parser class name
    """
    registry = get_registry()
    parsers = registry.list_parsers()
    
    logger.info(f"Listing parsers: {parsers}")
    
    return RegistryResponse(parsers=parsers)

