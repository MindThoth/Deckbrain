# Database Schema

This document describes the Core API database schema for DeckBrain. The schema is designed to support multiple plotter vendors through normalized data structures with vendor-specific metadata fields.

## Core Tables

### `devices`

Stores information about each vessel/device that connects to DeckBrain.

**Fields:**
- `id` (integer primary key)
- `device_id` (string, unique, indexed): Unique identifier for the vessel/device
- `name` (string, nullable): Human-readable vessel name or label
- `plotter_type` (string, not null): Identifies the primary navigation/fishing system this device is attached to
  - Examples: `"olex"`, `"maxsea"`, `"other"`
  - Used by Core API to route files to appropriate ingestion modules
  - Displayed in Dashboard as metadata (e.g., "source: Olex")
- `api_key_hash` (string, nullable): Hashed authentication key for the connector
- `created_at` (timestamp with timezone)
- `updated_at` (timestamp with timezone)
- `last_seen_at` (timestamp with timezone, nullable): Updated on each heartbeat
- Additional metadata fields as needed

**Notes:**
- The `plotter_type` field allows the Core API to understand which vendor's data format to expect
- Multiple connectors (different vendors) can feed into the same normalized schema by using this field
- When a connector registers or sends heartbeats, it includes its `plotter_type`

### `file_records`

Tracks all files uploaded from connectors.

**Fields:**
- `id` (integer primary key)
- `device_id` (foreign key to devices.id, indexed)
- `file_type` (string, not null): Logical type of the file content
  - Examples: `"track"`, `"soundings"`, `"marks"`, `"backup"`, `"unknown"`
  - Helps categorize files before parsing
- `source_format` (string, not null): Indicates the original file format for parsing
  - Examples: `"olex_raw"`, `"maxsea_mf2"`, `"tz_backup"`, `"unknown"`
  - Used by Core API to select the correct ingestion module
  - Olex Pi connector typically sets `source_format="olex_raw"`
  - MaxSea connector uses values like `"maxsea_mf2"` or `"tz_backup"` depending on file type
- `local_path` (string, nullable): Path where the file is stored on disk
- `remote_path` (string, nullable): Object storage path (future, when S3/GCS is implemented)
- `size_bytes` (integer, nullable): File size in bytes
- `processing_status` (string, not null, default "pending"): Processing status of the file
  - `"pending"`: File queued for upload (not yet uploaded)
  - `"stored"`: File successfully uploaded and stored, awaiting ingestion
  - `"processing"`: File is currently being parsed by an ingestion module
  - `"parsed_stub"`: File successfully parsed (stub only - no real entities extracted yet)
  - `"processed"`: File successfully parsed and entities extracted (future - when real parsing is implemented)
  - `"failed"`: Parsing failed or no parser available
- `uploaded_at` (timestamp with timezone)
- Additional metadata as needed

**Notes:**
- Parsing modules use `source_format` to know how to interpret raw files
- The `file_type` field helps with initial categorization before detailed parsing
- Files are stored on disk, and `file_records` tracks metadata and processing status

### `heartbeats`

Records periodic status updates from connectors.

**Fields:**
- `id` (integer primary key)
- `device_id` (foreign key to devices.id, indexed)
- `queue_size` (integer, nullable): Number of pending files in connector's local queue
- `last_upload_ok` (boolean, nullable): Whether the last upload attempt succeeded
- `connector_version` (string, nullable): Version of the connector software
- `received_at` (timestamp with timezone)
- Additional status fields as needed

**Notes:**
- Used by Dashboard to show live status (last sync time, queue size, connector health)
- Helps identify vessels with sync issues or outdated connectors

### `trips`

Normalized trip records (plotter-agnostic).

**Fields:**
- `id` (primary key)
- `device_id` (foreign key to devices)
- `start_time` (timestamp)
- `end_time` (timestamp, nullable)
- `name` (string, optional): Trip name or identifier
- Additional trip metadata

**Notes:**
- Trips are created by ingestion modules from raw plotter files
- All plotters contribute to the same trips table using normalized structure

### `tows`

Normalized tow segments within trips.

**Fields:**
- `id` (primary key)
- `trip_id` (foreign key to trips)
- `start_time` (timestamp)
- `end_time` (timestamp, nullable)
- `start_lat`, `start_lon` (float): Starting coordinates
- `end_lat`, `end_lon` (float, nullable): Ending coordinates
- Additional tow metadata

**Notes:**
- Tows are subsections of trips, identified by ingestion modules
- Normalized across all plotter sources

### `soundings`

Normalized depth readings.

**Fields:**
- `id` (primary key)
- `device_id` (foreign key to devices)
- `trip_id` (foreign key to trips, nullable)
- `tow_id` (foreign key to tows, nullable)
- `latitude` (float)
- `longitude` (float)
- `depth` (float): Depth reading
- `timestamp` (timestamp)
- Additional metadata

**Notes:**
- All depth readings from all plotters are stored in this normalized table
- Can be linked to trips/tows for context

### `marks`

Normalized waypoints and fishing marks.

**Fields:**
- `id` (primary key)
- `device_id` (foreign key to devices)
- `latitude` (float)
- `longitude` (float)
- `name` (string, optional)
- `mark_type` (string): `"waypoint"`, `"fishing_mark"`, `"custom"`, etc.
- `created_at` (timestamp)
- Additional metadata

**Notes:**
- Normalized marks from all plotter sources

### `tow_notes`

User-entered notes and log photos (plotter-agnostic).

**Fields:**
- `id` (primary key)
- `device_id` (foreign key to devices)
- `trip_id` (foreign key to trips, nullable)
- `tow_id` (foreign key to tows, nullable)
- `note_text` (text, optional): Typed note
- `image_path` (string, optional): Path to uploaded log photo
- `created_at` (timestamp)
- `created_by` (string, optional): User identifier

**Notes:**
- Tow notes are entered via Dashboard, not from plotter files
- Plotter-agnostic feature

## Relationships

- `devices` → `file_records` (one-to-many)
- `devices` → `heartbeats` (one-to-many)
- `devices` → `trips` (one-to-many)
- `trips` → `tows` (one-to-many)
- `trips` → `soundings` (one-to-many, optional)
- `tows` → `soundings` (one-to-many, optional)
- `devices` → `marks` (one-to-many)
- `trips` → `tow_notes` (one-to-many, optional)
- `tows` → `tow_notes` (one-to-many, optional)

## Multi-Plotter Support

The schema supports multiple plotter vendors through:

1. **`devices.plotter_type`**: Identifies which vendor's connector is attached to the device
2. **`file_records.source_format`**: Indicates the original file format for routing to ingestion modules
3. **Normalized tables** (`trips`, `tows`, `soundings`, `marks`): All plotter data is converted into common structures

This design allows:
- Multiple connectors (different vendors) to feed into the same normalized schema
- Vessels to switch plotters without losing historical data
- Fleet managers to view data from vessels using different plotter systems
- Future plotter integrations without schema changes

