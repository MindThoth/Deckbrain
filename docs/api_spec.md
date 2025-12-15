# Core API Specification

This document describes the Core API endpoints used by DeckBrain connectors and clients. The API is designed to be vendor-agnostic, meaning all plotter connectors (Olex, MaxSea, and others) use the same protocol.

## Authentication

All connector endpoints require authentication using HTTP headers:

- `X-Device-ID`: Unique device identifier
- `X-API-Key`: Authentication key for the device

The Core API validates these credentials against the `devices` table and uses `device.plotter_type` to understand which vendor's data format to expect.

## Vendor-Agnostic Connector Protocol

All connectors, regardless of vendor (Olex Pi, MaxSea Windows, etc.), must follow the same protocol:

1. **Authentication**: Send `device_id` and `api_key` in headers for all requests
2. **File Upload**: Call `POST /api/upload_file` to upload files
3. **Status Reporting**: Call `POST /api/heartbeat` to report status
4. **Update Checks**: Optionally call `GET /api/check_update` to check for new connector versions

The server uses device configuration (including `plotter_type` from the `devices` table) to understand what vendor the data originated from. Connectors do not need to specify vendor information in request bodies; the server determines this from the authenticated device.

## Endpoints

### GET `/health`

Basic service health check endpoint.

**Headers:** None required

**Response:**
```json
{
  "status": "ok",
  "service": "core-api",
  "version": "0.2.0-dev"
}
```

**Notes:**
- Used by monitoring systems and load balancers
- Does not require authentication
- Future: Will include database and storage connectivity checks

### GET `/api/devices`

Lists all registered devices (placeholder).

**Headers:**
- TODO: Will require authentication in future

**Query Parameters:** None (future: pagination, filtering)

**Response:**
```json
{
  "devices": [],
  "total": 0
}
```

**Notes:**
- Currently returns empty list (placeholder)
- Future: Will query devices table and return real device data
- Future: Add pagination, filtering by plotter_type, status

### GET `/api/devices/{device_id}`

Get details for a specific device (placeholder).

**Headers:**
- TODO: Will require authentication in future

**Path Parameters:**
- `device_id` (string): Unique device identifier

**Response:**
```json
{
  "device_id": "device123",
  "vessel_name": "Placeholder Vessel",
  "plotter_type": "olex",
  "last_heartbeat_at": null
}
```

**Notes:**
- Currently returns placeholder data
- Future: Will query devices table and return 404 if not found

### POST `/api/heartbeat`

Receive periodic status updates from connectors. **Authentication required.**

**Headers:**
- `X-Device-ID` (required): Unique device identifier
- `X-API-Key` (required): API key for authentication
- `X-Plotter-Type` (optional): Plotter type (olex, maxsea, etc.) - only used for auto-registration in dev mode

**Body:**
```json
{
  "queue_size": 5,
  "last_upload_ok": true,
  "connector_version": "0.1.0"
}
```

**Success Response:**
```json
{
  "status": "ok",
  "device_id": "device123",
  "received_at": "2025-12-12T10:30:00Z"
}
```

**Error Responses:**
```json
{
  "detail": "Missing required header: X-Device-ID"
}
```
```json
{
  "detail": "Invalid API key for device"
}
```

**Notes:**
- **Authentication is now enforced**: Device must be registered with a valid API key
- In development mode, device is auto-created on first request
- In production mode, devices must be pre-registered
- Updates device.last_seen_at timestamp on every heartbeat
- Stores heartbeat record in database for monitoring

### POST `/api/upload_file`

Uploads a raw plotter file to the Core API. **Authentication required.**

This is a vendor-agnostic endpoint used by all connector types (Olex, MaxSea, etc.). The server determines the plotter type from the authenticated device.

**Headers:**
- `X-Device-ID` (required): Unique device identifier
- `X-API-Key` (required): API key for authentication
- `X-Plotter-Type` (optional): Only used for auto-registration in development mode
- `Content-Type`: `multipart/form-data`

**Body (multipart/form-data):**
- `file` (required): The file to upload (binary)
- `file_type` (string, optional, default "unknown"): Logical type of file content
  - Examples: `"track"`, `"marks"`, `"soundings"`, `"backup"`, `"unknown"`
  - Helps with initial categorization
- `source_format` (string, optional, default "unknown"): File format hint
  - Examples: `"olex_raw"`, `"maxsea_mf2"`, `"tz_backup"`, `"unknown"`
  - Used by ingestion modules to parse files correctly
- `local_path` (string, optional): Path on connector's disk (for reference)
- `captured_at` (ISO datetime string, optional): When file was created/captured

**Success Response:**
```json
{
  "status": "ok",
  "file_record_id": 123,
  "remote_path": "devices/vessel-123/raw/2025/12/13/abc123__tracks.dat",
  "size_bytes": 45678,
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "processing_status": "stored"
}
```

**Error Responses:**
```json
{
  "detail": "Missing required header: X-Device-ID"
}
```
```json
{
  "detail": "Invalid API key for device"
}
```
```json
{
  "detail": "No file provided"
}
```

**Notes:**
- **Authentication is enforced**: Device must be registered (or in dev mode, auto-registered on first request)
- The Core API determines the vendor from `device.plotter_type` (not from request body)
- Files are stored under `storage/devices/<device_id>/raw/<yyyy>/<mm>/<dd>/<uuid>__<filename>`
- A `file_records` entry is created with sha256 hash for deduplication
- Processing status is initially "stored", then changed to "processed" or "failed" by ingestion modules
- This endpoint is used identically by Olex Pi, MaxSea Windows, and any future connectors

### POST `/api/heartbeat`

Sends periodic status updates from the connector.

**Headers:**
- `X-Device-ID`: Device identifier
- `X-API-Key`: Authentication key
- `Content-Type`: `application/json`

**Body:**
```json
{
  "queue_size": 5,
  "connector_version": "0.1.0",
  "last_sync_ok": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Heartbeat received"
}
```

**Notes:**
- Connectors should send heartbeats regularly (e.g., every 5 minutes)
- The server records heartbeats in the `heartbeats` table with `plotter_type` from `device.plotter_type`
- Used by Dashboard to show live status (last sync time, queue size, connector health)
- Same protocol for all connector types

### GET `/api/check_update`

Checks for available connector software updates.

**Headers:**
- `X-Device-ID`: Device identifier
- `X-API-Key`: Authentication key

**Query Parameters:**
- `current_version` (string, optional): Current connector version

**Response:**
```json
{
  "update_available": false,
  "latest_version": "0.1.0",
  "download_url": null
}
```

Or if update available:
```json
{
  "update_available": true,
  "latest_version": "0.2.0",
  "download_url": "https://...",
  "release_notes": "..."
}
```

**Notes:**
- The server uses `device.plotter_type` to determine which connector type to check updates for
- Future behavior: connectors will download and apply updates automatically
- Same endpoint for all connector types

### GET `/api/trips`

Lists trips for a device (plotter-agnostic).

**Headers:**
- `X-Device-ID`: Device identifier (or user authentication for Dashboard)
- `X-API-Key`: Authentication key (or user token for Dashboard)

**Query Parameters:**
- `device_id` (string, optional): Filter by device (for Dashboard/admin use)
- `start_date` (ISO date, optional): Filter trips starting after this date
- `end_date` (ISO date, optional): Filter trips ending before this date

**Response:**
```json
{
  "trips": [
    {
      "id": "uuid",
      "device_id": "device123",
      "start_time": "2025-12-01T08:00:00Z",
      "end_time": "2025-12-05T18:00:00Z",
      "name": "Trip 2025-12-01"
    }
  ]
}
```

**Notes:**
- Returns normalized trip data regardless of source plotter
- Dashboard uses this endpoint to display trips from any supported plotter

### GET `/api/tracks/{trip_id}`

Gets track data for a specific trip.

**Headers:**
- `X-Device-ID`: Device identifier (or user authentication)
- `X-API-Key`: Authentication key (or user token)

**Response:**
```json
{
  "trip_id": "uuid",
  "tracks": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "LineString",
          "coordinates": [[lon, lat], ...]
        },
        "properties": {
          "timestamp": "2025-12-01T08:00:00Z"
        }
      }
    ]
  }
}
```

**Notes:**
- Returns GeoJSON format, plotter-agnostic
- Dashboard renders this identically regardless of source plotter

### GET `/api/trips`

Lists trips for a device (plotter-agnostic).

**Query Parameters:**
- `device_id` (string, required): Filter by device
- `limit` (integer, optional, default 50, max 100): Maximum trips to return
- `offset` (integer, optional, default 0): Number of trips to skip for pagination

**Response:**
```json
{
  "trips": [
    {
      "id": 123,
      "device_id": 1,
      "start_time": "2025-12-10T08:00:00Z",
      "end_time": "2025-12-10T14:00:00Z",
      "name": "Morning Trip - Dec 10",
      "distance_nm": 12.5,
      "duration_hours": 6.0,
      "bounds": {
        "min_lat": 42.0,
        "max_lat": 42.2,
        "min_lon": -70.5,
        "max_lon": -70.3
      },
      "created_at": "2025-12-10T08:00:00Z"
    }
  ],
  "total": 10,
  "device_id": "test-vessel-001"
}
```

**Notes:**
- Returns trips sorted by start_time (most recent first)
- Trips are normalized across all plotter types

### GET `/api/trips/{trip_id}`

Gets detailed information for a specific trip.

**Path Parameters:**
- `trip_id` (integer): ID of the trip

**Response:**
```json
{
  "trip": {
    "id": 123,
    "device_id": 1,
    "start_time": "2025-12-10T08:00:00Z",
    "end_time": "2025-12-10T14:00:00Z",
    "name": "Morning Trip - Dec 10",
    "distance_nm": 12.5,
    "duration_hours": 6.0,
    "bounds": {
      "min_lat": 42.0,
      "max_lat": 42.2,
      "min_lon": -70.5,
      "max_lon": -70.3
    },
    "tows": [
      {
        "id": 456,
        "tow_number": 1,
        "name": "Tow 1",
        "start_time": "2025-12-10T09:00:00Z",
        "end_time": "2025-12-10T10:00:00Z",
        "distance_nm": 4.0,
        "duration_hours": 1.0,
        "avg_depth_m": 45.0,
        "min_depth_m": 35.0,
        "max_depth_m": 55.0
      }
    ]
  }
}
```

**Notes:**
- Includes list of tows within the trip

### GET `/api/trips/{trip_id}/track`

Gets track data for a trip in GeoJSON format.

**Path Parameters:**
- `trip_id` (integer): ID of the trip

**Query Parameters:**
- `include_tows` (boolean, optional, default false): Include tow boundary features

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [-70.45, 42.05],
          [-70.44, 42.06],
          ...
        ]
      },
      "properties": {
        "type": "track",
        "start_time": "2025-12-10T08:00:00Z",
        "end_time": "2025-12-10T14:00:00Z",
        "points_count": 360,
        "points": [
          {
            "timestamp": "2025-12-10T08:00:00Z",
            "depth": 45.0,
            "latitude": 42.05,
            "longitude": -70.45,
            "speed_knots": 4.0,
            "course_deg": 180.0,
            "water_temp": 10.0
          }
        ]
      }
    }
  ]
}
```

**Notes:**
- Returns GeoJSON FeatureCollection ready for map visualization
- Track data comes from soundings table
- Coordinates in [lon, lat] order (GeoJSON standard)

### GET `/api/trips/{trip_id}/tows/{tow_id}/track`

Gets track data for a specific tow in GeoJSON format.

**Path Parameters:**
- `trip_id` (integer): ID of the trip
- `tow_id` (integer): ID of the tow

**Response:**
Same format as `/api/trips/{trip_id}/track` but filtered to the specific tow.

## Additional Endpoints

Additional endpoints for history, tow notes, and other features will be documented as they are implemented. All endpoints follow the same vendor-agnostic design: they work with normalized data structures and do not require plotter-specific logic.

## Protocol Summary

**Key Points:**
- All connectors use the same endpoints and authentication method
- Vendor identification comes from `device.plotter_type` in the database, not from request bodies
- The API returns normalized data structures that work with any plotter source
- Olex is the first supported connector, but MaxSea and others will follow the exact same protocol
- No vendor-specific endpoints or logic required

