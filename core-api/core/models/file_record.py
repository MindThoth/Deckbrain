"""
DeckBrain Core API - FileRecord model.

Tracks uploaded files from connectors.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.db import Base


class FileRecord(Base):
    """
    FileRecord model.
    
    Tracks all files uploaded from connectors, including metadata about
    file type, source format, storage location, and processing status.
    """
    __tablename__ = "file_records"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to device
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    
    # File classification
    file_type = Column(String, nullable=False)  # track|soundings|marks|backup|unknown
    source_format = Column(String, nullable=False)  # olex_raw|maxsea_mf2|tz_backup|unknown
    
    # File storage
    local_path = Column(String, nullable=True)  # path on connector's disk
    remote_path = Column(String, nullable=True)  # path in Core API storage
    size_bytes = Column(Integer, nullable=True)  # file size
    sha256 = Column(String, nullable=True, index=True)  # file hash for deduplication
    
    # Processing status
    processing_status = Column(String, nullable=False, default="pending")  # pending|stored|processed|failed
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # when file was received
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # legacy, same as received_at
    
    # Relationship
    device = relationship("Device", back_populates="file_records")
    
    def __repr__(self):
        return f"<FileRecord(device_id={self.device_id}, file_type='{self.file_type}', status='{self.processing_status}')>"

