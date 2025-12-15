"""
DeckBrain Core API - Trip model.

Tracks vessel trips (normalized across all plotter types).
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.db import Base


class Trip(Base):
    """
    Trip model.
    
    Represents a vessel journey (start to end). Trips are created by ingestion
    modules from raw plotter files and are normalized across all plotter types.
    """
    __tablename__ = "trips"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to device
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    
    # Trip timing
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Trip metadata
    name = Column(String, nullable=True)  # Optional trip name or identifier
    
    # Geographic bounds (computed from track points)
    min_lat = Column(Float, nullable=True)
    max_lat = Column(Float, nullable=True)
    min_lon = Column(Float, nullable=True)
    max_lon = Column(Float, nullable=True)
    
    # Statistics
    distance_nm = Column(Float, nullable=True)  # Distance in nautical miles
    duration_hours = Column(Float, nullable=True)  # Duration in hours
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    device = relationship("Device", back_populates="trips")
    tows = relationship("Tow", back_populates="trip", cascade="all, delete-orphan")
    soundings = relationship("Sounding", back_populates="trip", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Trip(id={self.id}, device_id={self.device_id}, start_time={self.start_time}, name='{self.name}')>"

