# DeckBrain Connectors

Vendor-specific connector agents that run on vessels to collect plotter data and upload it to the Core API.

## Architecture

**Shared Core** (`shared/`): Common functionality for all connectors
- Configuration loading (device_id, api_key, server_url, plotter_type)
- SQLite queue management (offline-first operation)
- HTTP client (file uploads with retries and exponential backoff)
- Heartbeat sender (status updates with queue size, version)
- Update checker (checks for connector software updates)
- Logging helpers and version management

**Vendor-Specific Connectors**:
- `olex_pi/` - Olex Raspberry Pi connector (Linux/Pi sidecar device)
- `maxsea_win/` - MaxSea TimeZero Windows connector (Windows service)

## Common Protocol

All connectors use the same Core API endpoints:
- `POST /api/upload_file` - Upload raw plotter files
- `POST /api/heartbeat` - Send status updates
- `GET /api/check_update` - Check for updates

Authentication: `X-Device-ID` and `X-API-Key` headers.

## Status

Scaffolding only. Implementation will be added in future phases.

For details on the shared core, see `shared/README.md`.
