"""
GeoJSON utilities for track data.

Converts trip and sounding data to GeoJSON format for map visualization.
"""

from typing import List, Dict, Any
from datetime import datetime

from core.models import Trip, Tow, Sounding


def soundings_to_geojson(soundings: List[Sounding]) -> Dict[str, Any]:
    """
    Convert a list of soundings to a GeoJSON FeatureCollection.
    
    Args:
        soundings: List of Sounding objects
        
    Returns:
        GeoJSON FeatureCollection with LineString geometry
    """
    if not soundings:
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    # Sort soundings by timestamp
    sorted_soundings = sorted(soundings, key=lambda s: s.timestamp)
    
    # Build coordinates array [lon, lat] (GeoJSON order)
    coordinates = [
        [sounding.longitude, sounding.latitude]
        for sounding in sorted_soundings
    ]
    
    # Build properties for each point (for detailed view)
    point_properties = [
        {
            "timestamp": sounding.timestamp.isoformat(),
            "depth": sounding.depth,
            "latitude": sounding.latitude,
            "longitude": sounding.longitude,
            "speed_knots": sounding.speed_knots,
            "course_deg": sounding.course_deg,
            "water_temp": sounding.water_temp
        }
        for sounding in sorted_soundings
    ]
    
    # Create LineString feature for the track
    track_feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates
        },
        "properties": {
            "type": "track",
            "start_time": sorted_soundings[0].timestamp.isoformat(),
            "end_time": sorted_soundings[-1].timestamp.isoformat(),
            "points_count": len(sorted_soundings),
            "points": point_properties  # Include all point data
        }
    }
    
    return {
        "type": "FeatureCollection",
        "features": [track_feature]
    }


def tow_to_geojson_feature(tow: Tow) -> Dict[str, Any]:
    """
    Convert a Tow to a GeoJSON Feature.
    
    Args:
        tow: Tow object
        
    Returns:
        GeoJSON Feature with LineString geometry (if start/end coords exist)
    """
    # Build properties
    properties = {
        "type": "tow",
        "tow_id": tow.id,
        "tow_number": tow.tow_number,
        "name": tow.name,
        "start_time": tow.start_time.isoformat() if tow.start_time else None,
        "end_time": tow.end_time.isoformat() if tow.end_time else None,
        "distance_nm": tow.distance_nm,
        "duration_hours": tow.duration_hours,
        "avg_depth_m": tow.avg_depth_m,
        "min_depth_m": tow.min_depth_m,
        "max_depth_m": tow.max_depth_m
    }
    
    # Build geometry (simple line from start to end)
    geometry = None
    if (tow.start_lat is not None and tow.start_lon is not None and
        tow.end_lat is not None and tow.end_lon is not None):
        geometry = {
            "type": "LineString",
            "coordinates": [
                [tow.start_lon, tow.start_lat],
                [tow.end_lon, tow.end_lat]
            ]
        }
    
    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": properties
    }


def trip_to_summary_dict(trip: Trip) -> Dict[str, Any]:
    """
    Convert a Trip to a summary dictionary (for trip list endpoint).
    
    Args:
        trip: Trip object
        
    Returns:
        Dictionary with trip summary data
    """
    return {
        "id": trip.id,
        "device_id": trip.device_id,
        "start_time": trip.start_time.isoformat() if trip.start_time else None,
        "end_time": trip.end_time.isoformat() if trip.end_time else None,
        "name": trip.name,
        "distance_nm": trip.distance_nm,
        "duration_hours": trip.duration_hours,
        "bounds": {
            "min_lat": trip.min_lat,
            "max_lat": trip.max_lat,
            "min_lon": trip.min_lon,
            "max_lon": trip.max_lon
        } if trip.min_lat is not None else None,
        "created_at": trip.created_at.isoformat() if trip.created_at else None
    }


def trip_to_detail_dict(trip: Trip, include_tows: bool = True) -> Dict[str, Any]:
    """
    Convert a Trip to a detailed dictionary (for trip detail endpoint).
    
    Args:
        trip: Trip object (should be loaded with relationships if include_tows=True)
        include_tows: Whether to include tow summary data
        
    Returns:
        Dictionary with detailed trip data
    """
    result = trip_to_summary_dict(trip)
    
    if include_tows and hasattr(trip, 'tows'):
        result["tows"] = [
            {
                "id": tow.id,
                "tow_number": tow.tow_number,
                "name": tow.name,
                "start_time": tow.start_time.isoformat() if tow.start_time else None,
                "end_time": tow.end_time.isoformat() if tow.end_time else None,
                "distance_nm": tow.distance_nm,
                "duration_hours": tow.duration_hours,
                "avg_depth_m": tow.avg_depth_m,
                "min_depth_m": tow.min_depth_m,
                "max_depth_m": tow.max_depth_m
            }
            for tow in sorted(trip.tows, key=lambda t: t.start_time)
        ]
    
    return result

