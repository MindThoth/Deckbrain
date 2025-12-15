# Shared Connector Core

Common functionality used by all vendor-specific connectors (Olex Pi, MaxSea Windows, and future connectors).

## What This Provides

- **Configuration**: Loads device_id, api_key, server_url, plotter_type from config
- **SQLite Queue**: Local file queue for offline-first operation
- **HTTP Client**: Uploads files to Core API with retries and exponential backoff
- **Heartbeat**: Sends periodic status updates (queue size, version, last sync status)
- **Update Checker**: Checks `/api/check_update` for connector software updates
- **Logging**: Consistent logging helpers
- **Version**: Reads and manages connector version from version.json

## Usage

Vendor connectors import from this shared core:

```python
from shared.config import load_config
from shared.queue import FileQueue
from shared.http_client import upload_file
from shared.heartbeat import send_heartbeat
```

This avoids duplicating queue, HTTP, and heartbeat logic across connectors.

## Status

Scaffolding only. Implementation will be added in future development phases.

