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

### POST `/api/upload_file`

Uploads a raw plotter file to the Core API.

**Headers:**
- `X-Device-ID`: Device identifier
- `X-API-Key`: Authentication key
- `Content-Type`: `multipart/form-data`

**Body (multipart/form-data):**
- `file`: The file to upload (binary)
- `file_type` (string, optional): Logical type of file content
  - Examples: `"track"`, `"marks"`, `"soundings"`, `"backup"`, `"unknown"`
  - Helps with initial categorization
  - The Core API primarily uses `device.plotter_type` and `file_records.source_format` for routing, not this field

**Response:**
```json
{
  "success": true,
  "file_id": "uuid",
  "message": "File uploaded successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

**Notes:**
- The Core API determines the vendor from `device.plotter_type` (not from request body)
- Files are stored under `storage/<device_id>/...`
- A `file_records` entry is created with `source_format` determined by the ingestion module based on `plotter_type` and file content
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

## Additional Endpoints

Additional endpoints for history, tow notes, and other features will be documented as they are implemented. All endpoints follow the same vendor-agnostic design: they work with normalized data structures and do not require plotter-specific logic.

## Protocol Summary

**Key Points:**
- All connectors use the same endpoints and authentication method
- Vendor identification comes from `device.plotter_type` in the database, not from request bodies
- The API returns normalized data structures that work with any plotter source
- Olex is the first supported connector, but MaxSea and others will follow the exact same protocol
- No vendor-specific endpoints or logic required

