# Multi-Plotter Connector Architecture

DeckBrain is designed to support multiple navigation and fishing plotter systems through vendor-specific connector agents. All connectors feed into a shared, plotter-agnostic Core API and Dashboard.

## Connector Family Structure

### Shared Core (`connector/shared/`)

All connector implementations share common functionality:

- **Configuration**: device_id, api_key, base URL, plotter_type
- **Queue Management**: SQLite-based local queue for offline-first operation
- **HTTP Client**: standardized upload protocol to Core API
- **Logging Helpers**: consistent logging across all connectors
- **Version Management**: reads version.json, checks for updates
- **Heartbeat Module**: sends periodic status updates with plotter_type

### Vendor-Specific Adapters

Each plotter vendor has its own adapter that handles vendor-specific details:

#### `connector/olex_pi/`
- **Platform**: Linux/Raspberry Pi
- **Responsibilities**:
  - Watches Olex export directories
  - Detects Olex-specific file formats
  - Parses Olex file structure (if needed for validation)
  - Uses shared core for queueing and upload
- **File Detection**: Monitors directories where Olex exports navigation and fishing data

#### `connector/maxsea_win/`
- **Platform**: Windows
- **Responsibilities**:
  - Watches MaxSea TimeZero export/backup directories
  - Detects MaxSea-specific file formats (e.g., .mf2 files)
  - Parses MaxSea file structure (if needed for validation)
  - Uses shared core for queueing and upload
- **File Detection**: Monitors MaxSea TimeZero backup/export locations

#### Future Connectors
- `connector/navnet/` – for Furuno NavNet systems
- `connector/wassp/` – for WASSP multibeam systems
- Additional vendors as needed

## Unified Upload Protocol

All connectors communicate with the Core API using the same endpoints:

### POST `/api/upload_file`
- Uploads raw plotter files with metadata:
  - `device_id`: unique vessel identifier
  - `api_key`: authentication token
  - `plotter_type`: vendor identifier (e.g., "olex", "maxsea")
  - `source_format`: file format identifier (e.g., "olex_raw", "maxsea_mf2")
  - File content (multipart/form-data)

### POST `/api/heartbeat`
- Sends periodic status updates:
  - `device_id`: vessel identifier
  - `api_key`: authentication token
  - `plotter_type`: vendor identifier
  - `queue_size`: number of pending files
  - `version`: connector version
  - `last_sync_ok`: boolean indicating last upload success

### GET `/api/check_update`
- Checks for connector software updates:
  - `device_id`: vessel identifier
  - `api_key`: authentication token
  - `plotter_type`: vendor identifier
  - `current_version`: installed connector version
- Returns update information if available

## Core API Vendor Distinction

The Core API distinguishes between vendors using database fields:

### `devices` Table
- `plotter_type`: string identifier (e.g., "olex", "maxsea", "navnet")
- Used to route files to appropriate ingestion modules
- Displayed in Dashboard as metadata (e.g., "source: Olex")

### `file_records` Table
- `source_format`: string identifier (e.g., "olex_raw", "maxsea_mf2")
- Indicates the original file format for parsing
- Used to select the correct ingestion module

## Ingestion Modules

The Core API uses vendor-specific ingestion modules to parse raw files into normalized DeckBrain objects:

### `core-api/modules/ingest_olex/`
- Parses Olex export files
- Converts to normalized structures:
  - **Trips**: groups track segments by date/vessel
  - **Tows**: identifies tow start/end points
  - **Soundings**: depth readings with coordinates
  - **Marks**: waypoints and fishing marks
- Outputs to shared `trips`, `tows`, `soundings`, `marks` tables

### `core-api/modules/ingest_maxsea/`
- Parses MaxSea TimeZero export files
- Converts to normalized structures (same as Olex):
  - **Trips**: groups track segments
  - **Tows**: identifies tow segments
  - **Soundings**: depth readings
  - **Marks**: waypoints and marks
- Outputs to shared normalized tables

### Future Ingestion Modules
- `ingest_navnet/` – Furuno NavNet format parser
- `ingest_wassp/` – WASSP multibeam data parser
- Additional parsers as new plotters are supported

## Normalized Data Model

All plotter data is converted into a common DeckBrain data model:

- **Trips**: vessel journeys with start/end times, regardless of source plotter
- **Tows**: fishing tow segments within trips
- **Soundings**: depth readings with lat/lon coordinates
- **Marks**: waypoints, fishing marks, and custom points
- **Tow Notes**: user-entered notes and log photos (plotter-agnostic)

The Dashboard operates entirely on these normalized structures and does not need to know the source plotter format.

## Architecture Diagram

```
┌─────────────┐         ┌──────────────┐
│   Olex     │         │   MaxSea     │
│  Plotter   │         │  TimeZero    │
└─────┬───────┘         └──────┬───────┘
      │                        │
      │ Export Files          │ Export Files
      │                        │
┌─────▼────────────────────────▼───────┐
│  connector/olex_pi/  │ connector/   │
│                      │ maxsea_win/  │
│  ┌────────────────────────────────┐ │
│  │   connector/shared/           │ │
│  │   - queue DB                   │ │
│  │   - HTTP client                │ │
│  │   - heartbeat                  │ │
│  └────────────────────────────────┘ │
└─────┬───────────────────────────────┘
      │
      │ POST /api/upload_file
      │ POST /api/heartbeat
      │ (plotter_type: "olex" | "maxsea")
      │
┌─────▼───────────────────────────────┐
│         Core API                     │
│                                      │
│  ┌──────────────┐  ┌──────────────┐│
│  │ ingest_olex │  │ ingest_maxsea││
│  └──────┬───────┘  └──────┬───────┘│
│         │                  │        │
│         └────────┬─────────┘        │
│                  │                  │
│         Normalized Data Model       │
│         (trips, tows, soundings)    │
└──────────────────┬──────────────────┘
                   │
                   │ GET /api/trips
                   │ GET /api/tracks
                   │ (plotter-agnostic)
                   │
         ┌─────────▼─────────┐
         │    Dashboard       │
         │  (Next.js Web App) │
         │                    │
         │  Works with        │
         │  normalized data   │
         │  from any plotter  │
         └────────────────────┘
```

## Dashboard Plotter-Agnostic Design

The Dashboard is designed to work with normalized data and does not need vendor-specific logic:

- **Trips View**: Displays trips from any plotter using the same normalized trip structure
- **Tracks**: Renders track lines identically regardless of source
- **History**: Aggregates data from multiple plotters (if a vessel switches systems)
- **Metadata Display**: May show plotter brand as informational metadata (e.g., "source: Olex") but does not require different rendering logic

This design allows:
- Vessels to switch plotters without losing historical data
- Fleet managers to view data from vessels using different plotter systems
- Future plotter integrations without Dashboard changes

## Adding a New Plotter

To add support for a new plotter system:

1. **Create Connector Adapter**: `connector/<vendor>_<platform>/`
   - Implement vendor-specific file watching
   - Use shared core for queueing and upload
   - Set `plotter_type` in configuration

2. **Create Ingestion Module**: `core-api/modules/ingest_<vendor>/`
   - Parse vendor-specific file formats
   - Convert to normalized DeckBrain structures
   - Register with Core API routing

3. **Update Database Schema** (if needed):
   - Add new `plotter_type` value to allowed list
   - Add new `source_format` identifiers

4. **Test Integration**:
   - Verify connector uploads files correctly
   - Verify ingestion produces normalized data
   - Verify Dashboard displays data correctly

No Dashboard changes are required for new plotter support.

