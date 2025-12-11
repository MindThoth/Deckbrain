# Shared Connector Core

This directory contains shared logic for all vendor-specific connectors.

## Purpose

The shared connector core provides common functionality that both Olex Pi and MaxSea Windows connectors (and future connectors) import and reuse:

- **Configuration Loading**: Reads config file containing device_id, api_key, server_url, plotter_type
- **SQLite Queue Management**: Maintains a local SQLite-based file queue for offline-first operation
- **HTTP Client**: Handles file uploads to the Core API with retries and exponential backoff
- **Heartbeat Sender**: Sends periodic status updates with queue size, last upload status, connector version
- **Update Checker**: Checks `/api/check_update` for available connector software updates (future behavior)
- **Logging Helpers**: Consistent logging across all connectors
- **Version Management**: Reads version.json, manages connector version

## Usage

Vendor-specific connectors (e.g., `connector/olex_pi/`, `connector/maxsea_win/`) import modules from this shared core rather than duplicating queue, HTTP, and heartbeat logic.

## Implementation Status

This is scaffolding only. Real implementation will be added in future development phases.

