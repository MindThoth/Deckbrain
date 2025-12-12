"""
DeckBrain Core API - Heartbeat model.

Records periodic status updates from connectors.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.db import Base


class Heartbeat(Base):
    """
    Heartbeat model.
    
    Stores periodic status updates from connectors including queue size,
    connector version, and sync status.
    """
    __tablename__ = "heartbeats"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to device
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    
    # Heartbeat data
    queue_size = Column(Integer, nullable=True)  # number of pending files in connector queue
    last_upload_ok = Column(Boolean, nullable=True)  # whether last upload succeeded
    connector_version = Column(String, nullable=True)  # connector software version
    
    # Timestamp
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    device = relationship("Device", back_populates="heartbeats")
    
    def __repr__(self):
        return f"<Heartbeat(device_id={self.device_id}, queue_size={self.queue_size}, received_at='{self.received_at}')>"

