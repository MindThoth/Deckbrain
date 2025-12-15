# DeckBrain Connectors

DeckBrain uses vendor-specific connector agents that run on the vessel to collect plotter data and upload it to the Core API. All connectors share a common core for queueing, HTTP, and heartbeat functionality.

## Architecture

DeckBrain follows a **shared core + vendor-specific adapters** pattern:

- **`connector/shared/`**: Common code for all connectors
  - Configuration loading
  - SQLite queue management
  - HTTP client with retries
  - Heartbeat sender
  - Update checker
  - Logging helpers

- **`connector/olex_pi/`**: Olex Raspberry Pi connector
  - Runs on Linux/Raspberry Pi sidecar device
  - Watches Olex export directories
  - Uses shared core for queueing and upload

- **`connector/maxsea_win/`**: MaxSea TimeZero Windows connector
  - Runs as Windows service
  - Watches MaxSea TimeZero export/backup directories
  - Uses shared core for queueing and upload

## Common Protocol

All connectors use the same protocol when talking to the Core API:
- `POST /api/upload_file` - Upload raw plotter files
- `POST /api/heartbeat` - Send status updates
- `GET /api/check_update` - Check for connector updates

Authentication uses `X-Device-ID` and `X-API-Key` headers.

## Implementation Status

Currently scaffolding only. Real implementation will be added in future development phases.

For details on the shared core, see `connector/shared/README.md`.
