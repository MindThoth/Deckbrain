"""
DeckBrain Core API - Sounding model.

Tracks depth readings with coordinates (normalized across all plotter types).
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.db import Base


class Sounding(Base):
    """
    Sounding model.
    
    Represents a depth reading at a specific location and time. Soundings
    are created by ingestion modules from raw plotter files and are normalized
    across all plotter types.
    """
    __tablename__ = "soundings"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True, index=True)
    tow_id = Column(Integer, ForeignKey("tows.id"), nullable=True, index=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Geographic coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Depth reading
    depth = Column(Float, nullable=False)  # Depth in meters
    
    # Optional metadata
    water_temp = Column(Float, nullable=True)  # Water temperature in Celsius
    speed_knots = Column(Float, nullable=True)  # Vessel speed in knots
    course_deg = Column(Float, nullable=True)  # Vessel course in degrees
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    device = relationship("Device", back_populates="soundings")
    trip = relationship("Trip", back_populates="soundings")
    tow = relationship("Tow", back_populates="soundings")
    
    # Composite index for efficient spatial/temporal queries
    __table_args__ = (
        Index('ix_soundings_device_timestamp', 'device_id', 'timestamp'),
        Index('ix_soundings_trip_timestamp', 'trip_id', 'timestamp'),
        Index('ix_soundings_location', 'latitude', 'longitude'),
    )
    
    def __repr__(self):
        return f"<Sounding(id={self.id}, timestamp={self.timestamp}, lat={self.latitude:.4f}, lon={self.longitude:.4f}, depth={self.depth:.1f}m)>"

