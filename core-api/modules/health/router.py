"""
DeckBrain Core API - Health check endpoints.

Provides basic service health and status information for monitoring.
"""

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns service status, name, and version.
    Used by monitoring systems and load balancers.
    
    TODO:
    - Add database connectivity check
    - Add storage availability check
    - Return more detailed health metrics
    """
    return HealthResponse(
        status="ok",
        service="core-api",
        version="0.2.0-dev",
    )

