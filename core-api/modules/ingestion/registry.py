"""
DeckBrain Core API - Parser registry.

Maps source_format identifiers to parser instances, enabling vendor-agnostic
ingestion orchestration.
"""

import logging
from typing import Dict, Optional

from core.models import FileRecord
from .parsers import BaseParser, OlexParser, MaxSeaParser

logger = logging.getLogger(__name__)


class ParserRegistry:
    """
    Registry for vendor-specific parsers.
    
    Maps source_format identifiers (e.g., "olex_raw", "maxsea_mf2") to parser instances.
    Provides lookup functionality for the ingestion service.
    """
    
    def __init__(self):
        """Initialize the parser registry with all available parsers."""
        self._parsers: Dict[str, BaseParser] = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Register all default parsers."""
        parsers = [
            OlexParser(),
            MaxSeaParser(),
        ]
        
        for parser in parsers:
            self.register(parser)
            logger.info(f"Registered parser: {parser.__class__.__name__} for source_format='{parser.source_format}'")
    
    def register(self, parser: BaseParser):
        """
        Register a parser for a specific source_format.
        
        Args:
            parser: Parser instance to register
        """
        source_format = parser.source_format
        if source_format in self._parsers:
            logger.warning(f"Overwriting existing parser for source_format='{source_format}'")
        self._parsers[source_format] = parser
    
    def get_parser(self, source_format: str) -> Optional[BaseParser]:
        """
        Get a parser for a specific source_format.
        
        Args:
            source_format: Source format identifier (e.g., "olex_raw")
            
        Returns:
            Parser instance if found, None otherwise
        """
        return self._parsers.get(source_format)
    
    def get_parser_for_file(self, file_record: FileRecord) -> Optional[BaseParser]:
        """
        Get the appropriate parser for a file record.
        
        This method first attempts direct source_format lookup, then falls back
        to checking each parser's can_parse() method.
        
        Args:
            file_record: FileRecord to find parser for
            
        Returns:
            Parser instance if one can handle the file, None otherwise
        """
        # Try direct lookup first
        parser = self.get_parser(file_record.source_format)
        if parser and parser.can_parse(file_record):
            logger.debug(f"Found parser via direct lookup: {parser.__class__.__name__} for source_format='{file_record.source_format}'")
            return parser
        
        # Fall back to checking all parsers
        for parser in self._parsers.values():
            if parser.can_parse(file_record):
                logger.debug(f"Found parser via can_parse(): {parser.__class__.__name__} for file_record_id={file_record.id}")
                return parser
        
        logger.warning(f"No parser found for file_record_id={file_record.id}, source_format='{file_record.source_format}'")
        return None
    
    def list_parsers(self) -> Dict[str, str]:
        """
        List all registered parsers.
        
        Returns:
            Dict mapping source_format to parser class name
        """
        return {
            source_format: parser.__class__.__name__
            for source_format, parser in self._parsers.items()
        }


# Global registry instance
_registry = ParserRegistry()


def get_parser_for_file(file_record: FileRecord) -> Optional[BaseParser]:
    """
    Get the appropriate parser for a file record (convenience function).
    
    Args:
        file_record: FileRecord to find parser for
        
    Returns:
        Parser instance if one can handle the file, None otherwise
    """
    return _registry.get_parser_for_file(file_record)


def get_registry() -> ParserRegistry:
    """
    Get the global parser registry instance.
    
    Returns:
        Global ParserRegistry instance
    """
    return _registry

