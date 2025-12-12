"""
DeckBrain Core API - Device model.

Represents vessels/connectors registered in the system.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.db import Base


class Device(Base):
    """
    Device/vessel model.
    
    Stores information about each vessel/connector that connects to DeckBrain.
    Each connector has a unique device_id and is associated with a plotter type.
    """
    __tablename__ = "devices"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Device identification (what connector sends)
    device_id = Column(String, unique=True, index=True, nullable=False)
    
    # Vessel metadata
    name = Column(String, nullable=True)  # vessel name or label
    plotter_type = Column(String, nullable=False)  # olex|maxsea|other
    
    # Authentication
    # TODO: Implement proper API key hashing and storage
    api_key_hash = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)  # updated on heartbeat
    
    # Relationships
    heartbeats = relationship("Heartbeat", back_populates="device")
    file_records = relationship("FileRecord", back_populates="device")
    
    def __repr__(self):
        return f"<Device(device_id='{self.device_id}', name='{self.name}', plotter_type='{self.plotter_type}')>"

