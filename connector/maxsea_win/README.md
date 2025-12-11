# MaxSea TimeZero Connector (Windows)

This connector runs on Windows (same PC as MaxSea or a dedicated Windows machine).

## Architecture

- **Platform**: Windows (native service)
- **Connection**: Runs on the same PC as MaxSea TimeZero, or on a dedicated Windows mini-PC
- **Purpose**: Watches MaxSea export/backup directories for new files and enqueues them using `connector/shared/`
- **Note**: Does NOT require a Raspberry Pi

## Responsibilities

- Watches MaxSea TimeZero export/backup directories for new/updated files (e.g., .mf2, .ptf files)
- Classifies files by file_type (e.g., track, marks, backup, unknown)
- Enqueues files into the shared SQLite queue with vendor="maxsea"
- Sends heartbeats and uses the shared HTTP protocol to upload data to DeckBrain Core API

## Implementation Status

This is scaffolding only. Real implementation will be added in future development phases.

