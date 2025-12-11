# Multi-Plotter Connector Architecture

DeckBrain is designed to support multiple navigation and fishing plotter systems (at least Olex and MaxSea TimeZero) via separate connector agents that all use a shared upload protocol and common Core API.

## Connector Directory Structure

```
connector/
  shared/      -> common queue, HTTP client, heartbeat, config, update logic
  olex_pi/     -> Raspberry Pi agent that reads Olex export directories
  maxsea_win/  -> Windows agent that reads MaxSea TimeZero export/backup directories
```

## Connector Family Structure

### Shared Core (`connector/shared/`)

The shared connector core provides common functionality used by all vendor-specific connectors:

**Responsibilities:**
- **Configuration Loading**: Reads config file containing device_id, api_key, server_url, plotter_type
- **SQLite Queue Management**: Maintains a local SQLite database queue of pending files with fields:
  - file path
  - file_type (track, soundings, marks, backup, unknown)
  - vendor (olex, maxsea, etc.)
  - status (pending, uploading, uploaded, error)
- **HTTP Client**: Handles file upload to Core API with retries and exponential backoff
- **Heartbeat Sender**: Sends periodic heartbeats with:
  - queue size
  - last upload status (ok/error)
  - connector version
  - plotter_type
- **Update Checker**: Checks `/api/check_update` for available connector software updates (future behavior)

Both Olex Pi and MaxSea Windows connectors import and reuse this shared code.

### Vendor-Specific Adapters

#### `connector/olex_pi/` - Olex Connector (Raspberry Pi)

**Platform**: Linux/Raspberry Pi (sidecar device)

**Architecture**: 
- Runs on a Raspberry Pi connected by network to the Olex unit
- Does NOT run on the Olex unit itself (Olex is a closed appliance)
- The Pi mounts or accesses Olex export directories over the network

**Responsibilities:**
- Watches Olex export directories for new/updated files
- Detects files containing tracks, soundings, marks, etc.
- Classifies files by a simple file_type:
  - `track`: navigation track data
  - `soundings`: depth soundings
  - `marks`: waypoints and fishing marks
  - `unknown`: unrecognized file types
- Enqueues files into the shared SQLite queue with vendor="olex"
- Lets shared logic handle upload and heartbeat

**File Detection**: Monitors directories where Olex exports navigation and fishing data

#### `connector/maxsea_win/` - MaxSea TimeZero Connector (Windows)

**Platform**: Windows (native service)

**Architecture**:
- Runs on Windows (same PC as MaxSea TimeZero, or a dedicated Windows mini-PC)
- Does NOT require a Raspberry Pi

**Responsibilities:**
- Watches MaxSea TimeZero export/backup directories for new/updated files
- Detects MaxSea-specific file formats such as:
  - `.mf2` files (MaxSea TimeZero format)
  - `.ptf` files (TimeZero project files)
  - Other TimeZero export formats
- Classifies files by file_type:
  - `track`: navigation track data
  - `marks`: waypoints and marks
  - `backup`: TimeZero backup files
  - `unknown`: unrecognized file types
- Enqueues files into the shared SQLite queue with vendor="maxsea"
- Uses the same shared upload and heartbeat logic as the Olex connector

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

Olex -> Olex Pi connector -> DeckBrain Core API -> DeckBrain Dashboard

MaxSea -> Windows connector -> DeckBrain Core API -> DeckBrain Dashboard

Both connectors use the same Core API endpoints and upload protocol, feeding into the same normalized data model.

## Dashboard Plotter-Agnostic Design

The Dashboard is plotter-agnostic and operates entirely on normalized data:

- **Only consumes normalized entities**: trips, tows, notes, and history layers
- **No vendor-specific logic**: Does not need to know whether data came from Olex, MaxSea, or any other plotter
- **Metadata display**: May show the plotter brand as metadata (e.g., "source: Olex", "source: MaxSea") for informational purposes, but its rendering and business logic do not depend on vendor format

This design ensures:
- Vessels can switch plotters without losing historical data
- Fleet managers can view data from vessels using different plotter systems in a unified interface
- Future plotter integrations require no Dashboard changes

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

