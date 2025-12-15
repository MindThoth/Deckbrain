# Ingestion Pipeline

This document describes the DeckBrain ingestion pipeline, which processes raw plotter files uploaded by connectors and converts them into normalized data structures.

## Overview

The ingestion pipeline separates file **upload** from file **parsing**:

1. **Upload Phase**: Connectors upload raw files to the Core API via `POST /api/upload_file`. Files are stored on disk and tracked in `file_records` with `processing_status="stored"`.

2. **Ingestion Phase**: The ingestion service processes stored files using vendor-specific parsers, extracting normalized entities (trips, tows, soundings, marks) and updating `processing_status`.

This separation ensures:
- Fast, reliable uploads (no parsing delays)
- Resilient parsing (retries, async processing)
- Clear status tracking at each stage

## Architecture

The ingestion layer uses a **vendor-agnostic orchestration** pattern with **vendor-specific parsers**:

```
File Record (stored)
    ↓
Ingestion Service (orchestration)
    ↓
Parser Registry (routing)
    ↓
Vendor Parser (Olex, MaxSea, etc.)
    ↓
Normalized Entities (trips, tows, soundings, marks)
```

### Components

#### 1. Ingestion Service (`modules/ingestion/service.py`)

The ingestion service orchestrates the entire parsing process:

1. Load `file_record` from database
2. Validate `processing_status == "stored"`
3. Resolve parser using registry and `source_format`
4. Update `processing_status = "processing"`
5. Call `parser.parse(file_record)`
6. Based on result:
   - Success: `processing_status = "parsed_stub"` (or `"processed"` when real parsing is implemented)
   - Failure: `processing_status = "failed"`
7. Log all steps clearly

**Key Functions:**
- `ingest_file(file_record_id, db)`: Main ingestion function (raises exceptions)
- `ingest_file_safe(file_record_id, db)`: Safe wrapper that catches exceptions and returns dict

#### 2. Parser Registry (`modules/ingestion/registry.py`)

The parser registry maps `source_format` identifiers to parser instances:

```python
source_format → Parser
"olex_raw"    → OlexParser
"maxsea_mf2"  → MaxSeaParser
...
```

The registry supports:
- Direct lookup by `source_format`
- Fallback to `parser.can_parse()` for flexible matching
- Listing all registered parsers

**Key Functions:**
- `get_parser_for_file(file_record)`: Find appropriate parser for a file
- `get_registry()`: Get global registry instance

#### 3. Parser Interface (`modules/ingestion/parsers/base.py`)

All vendor-specific parsers implement the `BaseParser` abstract class:

```python
class BaseParser(ABC):
    @property
    @abstractmethod
    def source_format(self) -> str:
        """Source format identifier (e.g., "olex_raw")"""
        pass
    
    @abstractmethod
    def can_parse(self, file_record: FileRecord) -> bool:
        """Check if parser can handle this file"""
        pass
    
    @abstractmethod
    def parse(self, file_record: FileRecord) -> ParseResult:
        """Parse file and return normalized entities"""
        pass
```

**ParseResult:**
```python
@dataclass
class ParseResult:
    success: bool                      # Whether parsing succeeded
    message: str                       # Human-readable message
    parsed_entities: List[Dict]        # Extracted entities (trips, tows, etc.)
    metadata: Optional[Dict] = None    # Optional parser metadata
```

#### 4. Vendor-Specific Parsers

Each plotter vendor has its own parser implementation:

- **OlexParser** (`modules/ingestion/parsers/olex.py`)
  - Handles `source_format="olex_raw"` and `"olex"`
  - **Currently a stub** - no real parsing yet
  - Returns successful ParseResult with no entities

- **MaxSeaParser** (`modules/ingestion/parsers/maxsea.py`)
  - Handles `source_format="maxsea"`, `"maxsea_mf2"`, `"maxsea_timezero"`, `"tz_backup"`
  - **Currently a stub** - no real parsing yet
  - Returns successful ParseResult with no entities

**Future parsers:**
- NavNet parser
- WASSP parser
- etc.

## Automatic Ingestion (Dev Mode)

In **development mode** (`APP_ENV=development`), ingestion is automatically triggered after successful file upload:

**Flow:**
1. Connector uploads file → `POST /api/upload_file`
2. File saved to disk and `file_record` created with `processing_status="stored"`
3. **Auto-ingestion triggered** (synchronously in dev mode)
4. Ingestion service parses file using stub parsers
5. `processing_status` updated to `"parsed_stub"` or `"failed"`
6. Upload response returned with final `processing_status`

**Key Behaviors:**
- **Upload always succeeds**: Ingestion failures do NOT block upload response
- **Synchronous in dev**: Ingestion runs in the same request (no background jobs yet)
- **Disabled in production**: Auto-ingestion only runs when `APP_ENV=development`
- **Clear logging**: All auto-ingestion steps logged with `[AUTO-INGEST]` prefix

**Why Dev-Only?**

In production, ingestion will use background job processing (Celery, AWS Lambda, etc.) to:
- Handle large files without blocking uploads
- Retry failed parsing attempts
- Scale independently from upload throughput

For now, synchronous dev-mode ingestion enables rapid testing of the end-to-end pipeline.

## Current Status (v0.2.x-dev)

The ingestion architecture is **fully implemented but parsers are stubs only**:

✅ **Implemented:**
- Ingestion service orchestration
- Parser registry and routing
- Base parser interface
- Stub parsers for Olex and MaxSea
- Manual ingestion trigger endpoint (`POST /api/ingest/{file_record_id}`)
- **Automatic ingestion in dev mode** ✅
- Processing status tracking

❌ **Not Yet Implemented:**
- Real Olex file parsing
- Real MaxSea file parsing
- Normalized entity extraction (trips, tows, soundings, marks)
- Background job processing for production

## Processing Status Flow

Files progress through the following statuses:

1. **`pending`**: File queued for upload (connector local queue)
2. **`stored`**: File uploaded to Core API, awaiting ingestion
3. **`processing`**: File currently being parsed
4. **`parsed_stub`**: File parsed successfully (stub only - no real data extracted)
5. **`processed`**: File parsed successfully and entities extracted *(future)*
6. **`failed`**: Parsing failed or no parser available

## Usage

### Manual Ingestion (Dev/Debug)

Trigger ingestion for a specific file:

```bash
curl -X POST http://localhost:8000/api/ingest/123
```

Response:
```json
{
  "status": "ok",
  "file_record_id": 123,
  "message": "STUB: Olex parsing not yet implemented. File validated but not parsed.",
  "parsed_entities_count": 0,
  "metadata": {
    "parser": "OlexParser",
    "stub": true,
    "file_record_id": 123,
    "source_format": "olex_raw"
  }
}
```

### List Available Parsers

```bash
curl http://localhost:8000/api/ingest/parsers
```

Response:
```json
{
  "parsers": {
    "olex_raw": "OlexParser",
    "maxsea": "MaxSeaParser"
  }
}
```

### Programmatic Usage

```python
from sqlalchemy.orm import Session
from modules.ingestion.service import ingest_file

# Trigger ingestion
result = ingest_file(file_record_id=123, db=db)

if result.success:
    print(f"Parsed {len(result.parsed_entities)} entities")
else:
    print(f"Parsing failed: {result.message}")
```

## Adding a New Parser

To add support for a new plotter vendor:

1. **Create parser class** in `modules/ingestion/parsers/<vendor>.py`:
   ```python
   from .base import BaseParser, ParseResult
   from core.models import FileRecord
   
   class MyVendorParser(BaseParser):
       @property
       def source_format(self) -> str:
           return "myvendor_format"
       
       def can_parse(self, file_record: FileRecord) -> bool:
           return file_record.source_format == "myvendor_format"
       
       def parse(self, file_record: FileRecord) -> ParseResult:
           # TODO: Implement real parsing
           return ParseResult(
               success=True,
               message="Parsed successfully",
               parsed_entities=[]
           )
   ```

2. **Register parser** in `modules/ingestion/registry.py`:
   ```python
   from .parsers.myvendor import MyVendorParser
   
   def _register_default_parsers(self):
       parsers = [
           OlexParser(),
           MaxSeaParser(),
           MyVendorParser(),  # Add here
       ]
       ...
   ```

3. **Export parser** in `modules/ingestion/parsers/__init__.py`:
   ```python
   from .myvendor import MyVendorParser
   
   __all__ = [
       ...
       "MyVendorParser",
   ]
   ```

That's it! The new parser will be automatically registered and available for ingestion.

## Design Principles

1. **No Auto-Magic**: Explicit routing via registry, explicit errors when parsers are missing
2. **Vendor-Agnostic Core**: Ingestion service knows nothing about vendor formats
3. **Vendor-Specific Parsers**: Each parser encapsulates format-specific logic
4. **No Breaking Changes**: Upload and heartbeat APIs remain unchanged
5. **Clear Logging**: Every step is logged for debugging and monitoring
6. **Fail Fast**: Invalid states (wrong status, missing parser) raise clear errors immediately

## Future Work

- **Real Parsing**: Implement actual Olex and MaxSea file format parsers
- **Entity Extraction**: Create trips, tows, soundings, and marks in database
- **Automatic Ingestion**: Trigger ingestion automatically after successful upload
- **Background Jobs**: Process files asynchronously using Celery or similar
- **Retry Logic**: Retry failed ingestion with exponential backoff
- **Deduplication**: Skip files already processed (using SHA256 hash)
- **Progress Tracking**: Report parsing progress for large files
- **Parser Versioning**: Track which parser version processed each file

## Related Documentation

- **API Specification**: `docs/api_spec.md` - API endpoints
- **Database Schema**: `docs/db_schema.md` - Database tables and processing_status values
- **Multi-Plotter Architecture**: `docs/architecture/multi_plotter_connectors.md` - Connector design

