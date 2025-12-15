"""
DeckBrain Core API - Trips endpoints.

Provides endpoints for listing and retrieving trip data (normalized across all plotter types).
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel

from core.db import get_db
from core.models import Device, Trip, Tow, Sounding
from .geojson_utils import (
    trip_to_summary_dict,
    trip_to_detail_dict,
    soundings_to_geojson,
    tow_to_geojson_feature
)

logger = logging.getLogger(__name__)
router = APIRouter()


class TripSummary(BaseModel):
    """Response model for trip summary."""
    id: int
    device_id: int
    start_time: Optional[str]
    end_time: Optional[str]
    name: Optional[str]
    distance_nm: Optional[float]
    duration_hours: Optional[float]
    bounds: Optional[dict]
    created_at: Optional[str]


class TripsListResponse(BaseModel):
    """Response model for trips list endpoint."""
    trips: List[dict]
    total: int
    device_id: Optional[str]


class TripDetailResponse(BaseModel):
    """Response model for trip detail endpoint."""
    trip: dict


class TrackGeoJSON(BaseModel):
    """Response model for trip track GeoJSON."""
    type: str
    features: List[dict]


@router.get("/trips", response_model=TripsListResponse)
async def list_trips(
    device_id: Optional[str] = Query(None, description="Filter by device_id"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of trips to return"),
    offset: int = Query(0, ge=0, description="Number of trips to skip"),
    db: Session = Depends(get_db)
):
    """
    List trips for a device.
    
    Returns trips sorted by start_time (most recent first).
    
    Query Parameters:
    - device_id: Filter trips by device_id (required for now)
    - limit: Maximum number of trips to return (default: 50, max: 100)
    - offset: Number of trips to skip for pagination (default: 0)
    
    Returns:
        TripsListResponse with list of trip summaries
        
    Raises:
        HTTPException 400: If device_id not provided
        HTTPException 404: If device not found
    """
    logger.info(f"Listing trips: device_id={device_id}, limit={limit}, offset={offset}")
    
    # For now, require device_id
    # TODO: Add authentication and get device from auth context
    if not device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="device_id query parameter is required"
        )
    
    # Verify device exists
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device not found: {device_id}"
        )
    
    # Query trips
    query = db.query(Trip).filter(Trip.device_id == device.id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and sorting
    trips = (
        query
        .order_by(Trip.start_time.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    logger.info(f"Found {total} trips for device {device_id}, returning {len(trips)}")
    
    # Convert to response format
    trips_data = [trip_to_summary_dict(trip) for trip in trips]
    
    return TripsListResponse(
        trips=trips_data,
        total=total,
        device_id=device_id
    )


@router.get("/trips/{trip_id}", response_model=TripDetailResponse)
async def get_trip_detail(
    trip_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific trip.
    
    Includes trip metadata and list of tows.
    
    Path Parameters:
    - trip_id: ID of the trip to retrieve
    
    Returns:
        TripDetailResponse with detailed trip data including tows
        
    Raises:
        HTTPException 404: If trip not found
    """
    logger.info(f"Fetching trip detail for trip_id={trip_id}")
    
    # Query trip with tows loaded
    trip = (
        db.query(Trip)
        .options(joinedload(Trip.tows))
        .filter(Trip.id == trip_id)
        .first()
    )
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip not found: {trip_id}"
        )
    
    logger.info(f"Found trip {trip_id}: {trip.name}, {len(trip.tows)} tows")
    
    # Convert to response format
    trip_data = trip_to_detail_dict(trip, include_tows=True)
    
    return TripDetailResponse(trip=trip_data)


@router.get("/trips/{trip_id}/track", response_model=TrackGeoJSON)
async def get_trip_track(
    trip_id: int,
    include_tows: bool = Query(False, description="Include tow boundary features"),
    db: Session = Depends(get_db)
):
    """
    Get track data for a trip in GeoJSON format.
    
    Returns a GeoJSON FeatureCollection containing:
    - LineString feature with the complete track (from soundings)
    - Optional: Tow boundary features (if include_tows=true)
    
    Path Parameters:
    - trip_id: ID of the trip
    
    Query Parameters:
    - include_tows: Whether to include tow boundary features (default: false)
    
    Returns:
        GeoJSON FeatureCollection with track data
        
    Raises:
        HTTPException 404: If trip not found or no track data available
    """
    logger.info(f"Fetching track for trip_id={trip_id}, include_tows={include_tows}")
    
    # Verify trip exists
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip not found: {trip_id}"
        )
    
    # Query soundings for this trip
    soundings = (
        db.query(Sounding)
        .filter(Sounding.trip_id == trip_id)
        .order_by(Sounding.timestamp)
        .all()
    )
    
    if not soundings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No track data available for trip {trip_id}"
        )
    
    logger.info(f"Found {len(soundings)} soundings for trip {trip_id}")
    
    # Convert soundings to GeoJSON
    geojson = soundings_to_geojson(soundings)
    
    # Optionally add tow features
    if include_tows:
        tows = db.query(Tow).filter(Tow.trip_id == trip_id).order_by(Tow.start_time).all()
        logger.info(f"Adding {len(tows)} tow features")
        
        for tow in tows:
            tow_feature = tow_to_geojson_feature(tow)
            geojson["features"].append(tow_feature)
    
    return geojson


@router.get("/trips/{trip_id}/tows/{tow_id}/track", response_model=TrackGeoJSON)
async def get_tow_track(
    trip_id: int,
    tow_id: int,
    db: Session = Depends(get_db)
):
    """
    Get track data for a specific tow in GeoJSON format.
    
    Returns a GeoJSON FeatureCollection with soundings for the specified tow.
    
    Path Parameters:
    - trip_id: ID of the trip
    - tow_id: ID of the tow
    
    Returns:
        GeoJSON FeatureCollection with tow track data
        
    Raises:
        HTTPException 404: If tow not found or no track data available
    """
    logger.info(f"Fetching track for tow_id={tow_id} in trip_id={trip_id}")
    
    # Verify tow exists and belongs to trip
    tow = (
        db.query(Tow)
        .filter(Tow.id == tow_id, Tow.trip_id == trip_id)
        .first()
    )
    
    if not tow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tow {tow_id} not found in trip {trip_id}"
        )
    
    # Query soundings for this tow
    soundings = (
        db.query(Sounding)
        .filter(Sounding.tow_id == tow_id)
        .order_by(Sounding.timestamp)
        .all()
    )
    
    if not soundings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No track data available for tow {tow_id}"
        )
    
    logger.info(f"Found {len(soundings)} soundings for tow {tow_id}")
    
    # Convert soundings to GeoJSON
    geojson = soundings_to_geojson(soundings)
    
    return geojson

