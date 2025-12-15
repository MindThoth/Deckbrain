"""
DeckBrain Core API - Olex parser stub.

This is a STUB implementation. No real Olex parsing is performed yet.
The parser validates it can handle Olex files but returns a "not implemented" result.
"""

import logging
from typing import List

from core.models import FileRecord
from .base import BaseParser, ParseResult

logger = logging.getLogger(__name__)


class OlexParser(BaseParser):
    """
    Parser for Olex raw plotter files.
    
    STUB IMPLEMENTATION: This parser currently does not parse real Olex data.
    It validates file records and returns a stub result indicating parsing is not yet implemented.
    """
    
    @property
    def source_format(self) -> str:
        """Return the source_format identifier for Olex files."""
        return "olex_raw"
    
    def can_parse(self, file_record: FileRecord) -> bool:
        """
        Check if this parser can handle the given file record.
        
        Args:
            file_record: FileRecord to check
            
        Returns:
            True if source_format matches "olex_raw" or "olex"
        """
        return file_record.source_format in ["olex_raw", "olex"]
    
    def parse(self, file_record: FileRecord) -> ParseResult:
        """
        Parse an Olex raw plotter file (STUB).
        
        This is a stub implementation that does not actually parse Olex files.
        It logs the attempt and returns a successful ParseResult with no entities.
        
        Args:
            file_record: FileRecord to parse
            
        Returns:
            ParseResult indicating stub behavior
        """
        logger.info(f"[STUB] OlexParser.parse() called for file_record_id={file_record.id}")
        logger.info(f"[STUB] File: {file_record.remote_path}, type={file_record.file_type}, format={file_record.source_format}")
        logger.info("[STUB] Real Olex parsing not yet implemented - returning stub result")
        
        return ParseResult(
            success=True,
            message="STUB: Olex parsing not yet implemented. File validated but not parsed.",
            parsed_entities=[],
            metadata={
                "parser": "OlexParser",
                "stub": True,
                "file_record_id": file_record.id,
                "source_format": file_record.source_format
            }
        )

