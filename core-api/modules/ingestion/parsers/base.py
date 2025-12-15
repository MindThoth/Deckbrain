"""
DeckBrain Core API - Base parser interface.

Defines the abstract interface that all vendor-specific parsers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from core.models import FileRecord


@dataclass
class ParseResult:
    """
    Result of parsing a raw plotter file.
    
    Attributes:
        success: Whether parsing completed successfully
        message: Human-readable message describing the result
        parsed_entities: List of entities extracted from the file (trips, tows, soundings, marks)
        metadata: Optional additional metadata from parsing
    """
    success: bool
    message: str
    parsed_entities: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class BaseParser(ABC):
    """
    Abstract base class for vendor-specific plotter file parsers.
    
    Each parser implementation handles a specific source_format (e.g., "olex_raw", "maxsea_mf2").
    Parsers are responsible for:
    1. Validating they can parse a given file
    2. Reading and interpreting the file format
    3. Extracting normalized entities (trips, tows, soundings, marks)
    4. Returning a ParseResult with success/failure status
    """
    
    @property
    @abstractmethod
    def source_format(self) -> str:
        """
        The source_format identifier this parser handles.
        
        Examples: "olex_raw", "maxsea_mf2", "maxsea_tz_backup"
        
        Returns:
            String identifier matching file_records.source_format
        """
        pass
    
    @abstractmethod
    def can_parse(self, file_record: FileRecord) -> bool:
        """
        Check if this parser can handle the given file record.
        
        Args:
            file_record: FileRecord to check
            
        Returns:
            True if this parser can handle the file, False otherwise
        """
        pass
    
    @abstractmethod
    def parse(self, file_record: FileRecord) -> ParseResult:
        """
        Parse a raw plotter file and extract normalized entities.
        
        Args:
            file_record: FileRecord to parse (includes remote_path, source_format, etc.)
            
        Returns:
            ParseResult with success status, message, and extracted entities
        """
        pass

