"""
DeckBrain Core API - MaxSea parser stub.

This is a STUB implementation. No real MaxSea parsing is performed yet.
The parser validates it can handle MaxSea files but returns a "not implemented" result.
"""

import logging
from typing import List

from core.models import FileRecord
from .base import BaseParser, ParseResult

logger = logging.getLogger(__name__)


class MaxSeaParser(BaseParser):
    """
    Parser for MaxSea TimeZero plotter files.
    
    STUB IMPLEMENTATION: This parser currently does not parse real MaxSea data.
    It validates file records and returns a stub result indicating parsing is not yet implemented.
    """
    
    @property
    def source_format(self) -> str:
        """Return the source_format identifier for MaxSea files."""
        return "maxsea"
    
    def can_parse(self, file_record: FileRecord) -> bool:
        """
        Check if this parser can handle the given file record.
        
        Args:
            file_record: FileRecord to check
            
        Returns:
            True if source_format matches MaxSea formats
        """
        maxsea_formats = ["maxsea", "maxsea_mf2", "maxsea_timezero", "tz_backup"]
        return file_record.source_format in maxsea_formats
    
    def parse(self, file_record: FileRecord) -> ParseResult:
        """
        Parse a MaxSea plotter file (STUB).
        
        This is a stub implementation that does not actually parse MaxSea files.
        It logs the attempt and returns a successful ParseResult with no entities.
        
        Args:
            file_record: FileRecord to parse
            
        Returns:
            ParseResult indicating stub behavior
        """
        logger.info(f"[STUB] MaxSeaParser.parse() called for file_record_id={file_record.id}")
        logger.info(f"[STUB] File: {file_record.remote_path}, type={file_record.file_type}, format={file_record.source_format}")
        logger.info("[STUB] Real MaxSea parsing not yet implemented - returning stub result")
        
        return ParseResult(
            success=True,
            message="STUB: MaxSea parsing not yet implemented. File validated but not parsed.",
            parsed_entities=[],
            metadata={
                "parser": "MaxSeaParser",
                "stub": True,
                "file_record_id": file_record.id,
                "source_format": file_record.source_format
            }
        )

