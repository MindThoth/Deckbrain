"""
DeckBrain Core API - Ingestion parsers.

This package contains vendor-specific parsers for converting raw plotter
files into normalized DeckBrain data structures.
"""

from .base import BaseParser, ParseResult
from .olex import OlexParser
from .maxsea import MaxSeaParser

__all__ = [
    "BaseParser",
    "ParseResult",
    "OlexParser",
    "MaxSeaParser",
]

