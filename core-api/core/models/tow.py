"""
DeckBrain Core API - Tow model.

Tracks fishing tow segments within trips.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.db import Base


class Tow(Base):
    """
    Tow model.
    
    Represents a fishing tow segment within a trip. Tows are subsections
    of trips identified by ingestion modules or user annotations.
    """
    __tablename__ = "tows"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to trip
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    
    # Tow timing
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Tow location (start and end points)
    start_lat = Column(Float, nullable=True)
    start_lon = Column(Float, nullable=True)
    end_lat = Column(Float, nullable=True)
    end_lon = Column(Float, nullable=True)
    
    # Tow metadata
    name = Column(String, nullable=True)  # Optional tow name/label
    tow_number = Column(Integer, nullable=True)  # Sequential number within trip
    
    # Statistics
    distance_nm = Column(Float, nullable=True)  # Distance in nautical miles
    duration_hours = Column(Float, nullable=True)  # Duration in hours
    avg_depth_m = Column(Float, nullable=True)  # Average depth in meters
    min_depth_m = Column(Float, nullable=True)  # Minimum depth in meters
    max_depth_m = Column(Float, nullable=True)  # Maximum depth in meters
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    trip = relationship("Trip", back_populates="tows")
    soundings = relationship("Sounding", back_populates="tow", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tow(id={self.id}, trip_id={self.trip_id}, start_time={self.start_time}, tow_number={self.tow_number})>"

