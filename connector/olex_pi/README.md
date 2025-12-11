# Olex Connector (Raspberry Pi)

This connector runs on a Raspberry Pi connected to an Olex unit via network.

## Architecture

- **Platform**: Linux/Raspberry Pi (sidecar device)
- **Connection**: Network connection to Olex unit (Olex is a closed appliance, so the connector does not run on the Olex unit itself)
- **Purpose**: Watches Olex export directories for new files and enqueues them using `connector/shared/`

## Responsibilities

- Watches Olex export directories for new/updated files (tracks, soundings, marks, etc.)
- Classifies files by a simple file_type (e.g., track, soundings, marks, unknown)
- Enqueues files into the shared SQLite queue with vendor="olex"
- Sends heartbeats and uses the shared HTTP protocol to upload data to DeckBrain Core API

## Implementation Status

This is scaffolding only. Real implementation will be added in future development phases.

