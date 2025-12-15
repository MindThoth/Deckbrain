"""
DeckBrain Core API - Ingestion service.

Orchestrates the parsing of raw plotter files. This service:
1. Loads file_records from the database
2. Validates processing status
3. Routes files to appropriate vendor-specific parsers
4. Updates processing status based on parse results
5. Logs all steps clearly
"""

import logging
from typing import Optional
from pathlib import Path

from sqlalchemy.orm import Session

from core.models import FileRecord
from core.config import settings
from .registry import get_parser_for_file
from .parsers import ParseResult

logger = logging.getLogger(__name__)


class IngestionError(Exception):
    """Base exception for ingestion errors."""
    pass


class FileNotFoundError(IngestionError):
    """Raised when a file_record is not found."""
    pass


class InvalidStatusError(IngestionError):
    """Raised when file_record has invalid processing_status for ingestion."""
    pass


class NoParserError(IngestionError):
    """Raised when no parser is available for a file_record."""
    pass


def ingest_file(file_record_id: int, db: Session) -> ParseResult:
    """
    Ingest a raw plotter file and parse it into normalized entities.
    
    This is the main ingestion orchestration function. It:
    1. Loads the file_record from the database
    2. Validates processing_status is "stored"
    3. Finds the appropriate parser using the registry
    4. Updates status to "processing"
    5. Calls the parser
    6. Updates status to "parsed_stub" (success) or "failed" (error)
    7. Logs all steps
    
    Args:
        file_record_id: ID of the FileRecord to ingest
        db: Database session
        
    Returns:
        ParseResult from the parser
        
    Raises:
        FileNotFoundError: If file_record_id doesn't exist
        InvalidStatusError: If file is not in "stored" status
        NoParserError: If no parser can handle the file
        IngestionError: For other ingestion failures
    """
    logger.info(f"Starting ingestion for file_record_id={file_record_id}")
    
    # Step 1: Load file_record from database
    file_record = db.query(FileRecord).filter(FileRecord.id == file_record_id).first()
    if not file_record:
        logger.error(f"FileRecord not found: id={file_record_id}")
        raise FileNotFoundError(f"FileRecord with id={file_record_id} not found")
    
    logger.info(f"Loaded file_record: id={file_record.id}, source_format='{file_record.source_format}', "
                f"file_type='{file_record.file_type}', status='{file_record.processing_status}'")
    
    # Step 2: Validate processing_status
    if file_record.processing_status != "stored":
        logger.warning(f"File_record {file_record_id} has status '{file_record.processing_status}', expected 'stored'. Skipping ingestion.")
        raise InvalidStatusError(
            f"FileRecord {file_record_id} has status '{file_record.processing_status}', expected 'stored'"
        )
    
    # Step 3: Resolve parser using registry
    logger.info(f"Looking up parser for source_format='{file_record.source_format}'")
    parser = get_parser_for_file(file_record)
    
    if not parser:
        logger.error(f"No parser found for file_record_id={file_record_id}, source_format='{file_record.source_format}'")
        
        # Update status to failed
        file_record.processing_status = "failed"
        db.commit()
        
        raise NoParserError(
            f"No parser available for source_format='{file_record.source_format}'"
        )
    
    logger.info(f"Found parser: {parser.__class__.__name__}")
    
    # Step 4: Update status to "processing"
    file_record.processing_status = "processing"
    db.commit()
    logger.info(f"Updated file_record {file_record_id} status to 'processing'")
    
    # Step 5: Call parser
    try:
        logger.info(f"Calling {parser.__class__.__name__}.parse() for file_record_id={file_record_id}")
        result = parser.parse(file_record)
        
        logger.info(f"Parser returned: success={result.success}, message='{result.message}'")
        logger.info(f"Parsed entities count: {len(result.parsed_entities)}")
        
        # Step 6: Update status based on result
        if result.success:
            # Note: We use "parsed_stub" instead of "processed" to indicate
            # that parsing succeeded but no real data was extracted (stub behavior)
            file_record.processing_status = "parsed_stub"
            logger.info(f"Parser succeeded. Updated file_record {file_record_id} status to 'parsed_stub'")
        else:
            file_record.processing_status = "failed"
            logger.warning(f"Parser failed. Updated file_record {file_record_id} status to 'failed'")
        
        db.commit()
        
        return result
        
    except Exception as e:
        # Step 6 (error path): Update status to failed
        logger.error(f"Parser raised exception for file_record_id={file_record_id}: {e}", exc_info=True)
        
        file_record.processing_status = "failed"
        db.commit()
        
        raise IngestionError(f"Parsing failed for file_record {file_record_id}: {str(e)}") from e


def ingest_file_safe(file_record_id: int, db: Session) -> dict:
    """
    Safe wrapper around ingest_file that catches exceptions and returns a dict.
    
    Useful for background jobs or API endpoints that need graceful error handling.
    
    Args:
        file_record_id: ID of the FileRecord to ingest
        db: Database session
        
    Returns:
        Dict with status, message, and optional result
    """
    try:
        result = ingest_file(file_record_id, db)
        return {
            "status": "success" if result.success else "failed",
            "file_record_id": file_record_id,
            "message": result.message,
            "parsed_entities_count": len(result.parsed_entities),
            "metadata": result.metadata
        }
    except FileNotFoundError as e:
        logger.error(f"ingest_file_safe: FileNotFoundError - {e}")
        return {
            "status": "error",
            "file_record_id": file_record_id,
            "message": str(e),
            "error_type": "FileNotFoundError"
        }
    except InvalidStatusError as e:
        logger.warning(f"ingest_file_safe: InvalidStatusError - {e}")
        return {
            "status": "error",
            "file_record_id": file_record_id,
            "message": str(e),
            "error_type": "InvalidStatusError"
        }
    except NoParserError as e:
        logger.error(f"ingest_file_safe: NoParserError - {e}")
        return {
            "status": "error",
            "file_record_id": file_record_id,
            "message": str(e),
            "error_type": "NoParserError"
        }
    except IngestionError as e:
        logger.error(f"ingest_file_safe: IngestionError - {e}")
        return {
            "status": "error",
            "file_record_id": file_record_id,
            "message": str(e),
            "error_type": "IngestionError"
        }
    except Exception as e:
        logger.error(f"ingest_file_safe: Unexpected error - {e}", exc_info=True)
        return {
            "status": "error",
            "file_record_id": file_record_id,
            "message": f"Unexpected error: {str(e)}",
            "error_type": "UnexpectedError"
        }

