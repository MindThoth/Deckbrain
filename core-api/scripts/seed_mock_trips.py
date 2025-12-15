"""
Seed script for mock trip data.

Creates sample trips, tows, and soundings for development and testing.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import random

from core.db import SessionLocal
from core.models import Device, Trip, Tow, Sounding


def create_mock_track_points(
    start_lat: float,
    start_lon: float,
    num_points: int,
    start_time: datetime,
    speed_knots: float = 5.0,
    avg_depth: float = 50.0
) -> list:
    """
    Generate mock track points for a trip or tow.
    
    Args:
        start_lat: Starting latitude
        start_lon: Starting longitude
        num_points: Number of track points to generate
        start_time: Starting timestamp
        speed_knots: Vessel speed in knots
        avg_depth: Average depth in meters
        
    Returns:
        List of sounding dicts
    """
    soundings = []
    lat = start_lat
    lon = start_lon
    
    # Speed in degrees per minute (approximate)
    lat_per_minute = (speed_knots / 60.0)  # 1 knot ≈ 1 nautical mile ≈ 1/60 degree
    lon_per_minute = lat_per_minute / abs(random.uniform(0.8, 1.2))  # Vary slightly
    
    for i in range(num_points):
        # Add some randomness to simulate real vessel movement
        lat += random.uniform(-lat_per_minute, lat_per_minute)
        lon += random.uniform(-lon_per_minute, lon_per_minute)
        
        # Generate depth with some variation
        depth = avg_depth + random.uniform(-10, 10)
        
        # Generate timestamp
        timestamp = start_time + timedelta(minutes=i)
        
        soundings.append({
            'latitude': lat,
            'longitude': lon,
            'depth': max(5.0, depth),  # Ensure positive depth
            'timestamp': timestamp,
            'speed_knots': speed_knots + random.uniform(-1, 1),
            'course_deg': random.uniform(0, 360),
            'water_temp': 10.0 + random.uniform(-2, 2)
        })
    
    return soundings


def seed_mock_data(db: Session):
    """
    Seed the database with mock trip data.
    """
    print("🌱 Seeding mock trip data...")
    
    # Check if device exists, create if not
    device = db.query(Device).filter(Device.device_id == "test-vessel-001").first()
    if not device:
        print("  Creating test device: test-vessel-001")
        from core.auth import hash_api_key
        device = Device(
            device_id="test-vessel-001",
            name="Test Vessel 001",
            plotter_type="olex",
            api_key_hash=hash_api_key("my-secret-key-123")
        )
        db.add(device)
        db.commit()
        db.refresh(device)
    else:
        print(f"  Found existing device: {device.device_id}")
    
    # Create mock trips
    print("\n  Creating mock trips...")
    
    # Trip 1: Simple day trip with 2 tows
    trip1_start = datetime(2025, 12, 10, 8, 0, 0)
    trip1 = Trip(
        device_id=device.id,
        start_time=trip1_start,
        end_time=trip1_start + timedelta(hours=6),
        name="Morning Trip - Dec 10",
        min_lat=42.0,
        max_lat=42.2,
        min_lon=-70.5,
        max_lon=-70.3,
        distance_nm=12.5,
        duration_hours=6.0
    )
    db.add(trip1)
    db.flush()
    
    # Tow 1 for Trip 1
    tow1_start = trip1_start + timedelta(hours=1)
    tow1_points = create_mock_track_points(
        start_lat=42.05,
        start_lon=-70.45,
        num_points=60,  # 1 hour of data (1 point per minute)
        start_time=tow1_start,
        speed_knots=4.0,
        avg_depth=45.0
    )
    
    tow1 = Tow(
        trip_id=trip1.id,
        start_time=tow1_start,
        end_time=tow1_start + timedelta(hours=1),
        start_lat=tow1_points[0]['latitude'],
        start_lon=tow1_points[0]['longitude'],
        end_lat=tow1_points[-1]['latitude'],
        end_lon=tow1_points[-1]['longitude'],
        name="Tow 1",
        tow_number=1,
        distance_nm=4.0,
        duration_hours=1.0,
        avg_depth_m=45.0,
        min_depth_m=35.0,
        max_depth_m=55.0
    )
    db.add(tow1)
    db.flush()
    
    # Add soundings for Tow 1
    for point in tow1_points:
        sounding = Sounding(
            device_id=device.id,
            trip_id=trip1.id,
            tow_id=tow1.id,
            **point
        )
        db.add(sounding)
    
    # Tow 2 for Trip 1
    tow2_start = trip1_start + timedelta(hours=3)
    tow2_points = create_mock_track_points(
        start_lat=42.10,
        start_lon=-70.40,
        num_points=90,  # 1.5 hours
        start_time=tow2_start,
        speed_knots=3.5,
        avg_depth=52.0
    )
    
    tow2 = Tow(
        trip_id=trip1.id,
        start_time=tow2_start,
        end_time=tow2_start + timedelta(hours=1, minutes=30),
        start_lat=tow2_points[0]['latitude'],
        start_lon=tow2_points[0]['longitude'],
        end_lat=tow2_points[-1]['latitude'],
        end_lon=tow2_points[-1]['longitude'],
        name="Tow 2",
        tow_number=2,
        distance_nm=5.25,
        duration_hours=1.5,
        avg_depth_m=52.0,
        min_depth_m=42.0,
        max_depth_m=62.0
    )
    db.add(tow2)
    db.flush()
    
    for point in tow2_points:
        sounding = Sounding(
            device_id=device.id,
            trip_id=trip1.id,
            tow_id=tow2.id,
            **point
        )
        db.add(sounding)
    
    print(f"    ✓ Created trip: {trip1.name} with 2 tows")
    
    # Trip 2: Longer afternoon trip
    trip2_start = datetime(2025, 12, 11, 13, 0, 0)
    trip2 = Trip(
        device_id=device.id,
        start_time=trip2_start,
        end_time=trip2_start + timedelta(hours=8),
        name="Afternoon Trip - Dec 11",
        min_lat=42.1,
        max_lat=42.4,
        min_lon=-70.6,
        max_lon=-70.2,
        distance_nm=18.0,
        duration_hours=8.0
    )
    db.add(trip2)
    db.flush()
    
    # Single long tow for Trip 2
    tow3_start = trip2_start + timedelta(hours=2)
    tow3_points = create_mock_track_points(
        start_lat=42.20,
        start_lon=-70.50,
        num_points=120,  # 2 hours
        start_time=tow3_start,
        speed_knots=4.5,
        avg_depth=60.0
    )
    
    tow3 = Tow(
        trip_id=trip2.id,
        start_time=tow3_start,
        end_time=tow3_start + timedelta(hours=2),
        start_lat=tow3_points[0]['latitude'],
        start_lon=tow3_points[0]['longitude'],
        end_lat=tow3_points[-1]['latitude'],
        end_lon=tow3_points[-1]['longitude'],
        name="Tow 1",
        tow_number=1,
        distance_nm=9.0,
        duration_hours=2.0,
        avg_depth_m=60.0,
        min_depth_m=50.0,
        max_depth_m=70.0
    )
    db.add(tow3)
    db.flush()
    
    for point in tow3_points:
        sounding = Sounding(
            device_id=device.id,
            trip_id=trip2.id,
            tow_id=tow3.id,
            **point
        )
        db.add(sounding)
    
    print(f"    ✓ Created trip: {trip2.name} with 1 tow")
    
    # Trip 3: Recent trip (yesterday)
    trip3_start = datetime.now() - timedelta(days=1)
    trip3_start = trip3_start.replace(hour=7, minute=0, second=0, microsecond=0)
    trip3 = Trip(
        device_id=device.id,
        start_time=trip3_start,
        end_time=trip3_start + timedelta(hours=5),
        name="Recent Trip - Yesterday",
        min_lat=42.15,
        max_lat=42.35,
        min_lon=-70.55,
        max_lon=-70.35,
        distance_nm=15.0,
        duration_hours=5.0
    )
    db.add(trip3)
    db.flush()
    
    # Add one tow
    tow4_start = trip3_start + timedelta(hours=1)
    tow4_points = create_mock_track_points(
        start_lat=42.25,
        start_lon=-70.45,
        num_points=75,  # 1.25 hours
        start_time=tow4_start,
        speed_knots=4.0,
        avg_depth=48.0
    )
    
    tow4 = Tow(
        trip_id=trip3.id,
        start_time=tow4_start,
        end_time=tow4_start + timedelta(hours=1, minutes=15),
        start_lat=tow4_points[0]['latitude'],
        start_lon=tow4_points[0]['longitude'],
        end_lat=tow4_points[-1]['latitude'],
        end_lon=tow4_points[-1]['longitude'],
        name="Tow 1",
        tow_number=1,
        distance_nm=5.0,
        duration_hours=1.25,
        avg_depth_m=48.0,
        min_depth_m=40.0,
        max_depth_m=56.0
    )
    db.add(tow4)
    db.flush()
    
    for point in tow4_points:
        sounding = Sounding(
            device_id=device.id,
            trip_id=trip3.id,
            tow_id=tow4.id,
            **point
        )
        db.add(sounding)
    
    print(f"    ✓ Created trip: {trip3.name} with 1 tow")
    
    # Commit all changes
    db.commit()
    
    print("\n✅ Mock data seeded successfully!")
    print(f"   - 3 trips created")
    print(f"   - 4 tows created")
    print(f"   - ~345 soundings created")
    print(f"\nYou can now test the trips API endpoints:")
    print(f"  GET /api/trips?device_id={device.device_id}")
    print(f"  GET /api/trips/<trip_id>")
    print(f"  GET /api/trips/<trip_id>/track")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_mock_data(db)
    finally:
        db.close()

