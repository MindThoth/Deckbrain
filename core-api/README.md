# Core API (FastAPI Backend)

DeckBrain's Core API is the backend service that receives uploads from vessel connectors (Olex Pi, MaxSea Windows, and future vendors), stores and normalizes fishing/navigation data, and serves dashboards and future mobile apps via a clean JSON API.

## How This Service Fits Into DeckBrain

The Core API is the central data hub of the DeckBrain platform:

- **Plotter-Agnostic Design**: Multiple connector types (Olex Pi, MaxSea Windows, and future vendors) send data using a common upload protocol. The Core API normalizes this data regardless of source plotter.

- **Data Storage**: Stores normalized entities including:
  - Devices (vessel/connector registration and metadata)
  - File records (raw plotter files with source format tracking)
  - Trips (vessel journeys, normalized across all plotters)
  - Tows (fishing tow segments within trips)
  - Soundings (depth readings with coordinates)
  - Marks (waypoints and fishing marks)
  - Tow notes (user-entered notes and log photos)
  - Heartbeats (connector status and health)

- **Dashboard Integration**: Powers the Dashboard's Trips, History, Live Status, and Notes features by providing a stable JSON API that works with data from any supported plotter system.

For details on how multi-vendor connectors integrate with the Core API, see `docs/architecture/multi_plotter_connectors.md`.

## Responsibilities

- **Device Authentication**: Authenticate device connectors using `device_id` and `api_key` headers
- **File Ingestion**: Receive raw file uploads from connectors and track them in `file_records` with `source_format` metadata
- **Status Tracking**: Store device heartbeats (status, queue size, connector version) for live monitoring
- **Data Normalization**: Run ingestion/parsing modules for vendor-specific formats (Olex, MaxSea, etc.) to convert raw files into normalized DeckBrain structures
- **API Endpoints**: Provide endpoints for:
  - Device summary and health
  - Listing trips and retrieving trip tracks (GeoJSON)
  - Listing tows and their notes
  - Creating tow notes (text and images, in future)
  - Historical coverage and marks
  - Update checks for connectors
- **Stable Contracts**: Expose a stable, versionable JSON contract for the Dashboard and future mobile apps, independent of source plotter

## Directory Structure

```
core-api/
  core/           - Shared settings, database initialization, security helpers, common utilities
  modules/        - Feature modules:
                    - devices/     - Device registration, API key management, summary endpoints
                    - sync/        - Upload and heartbeat handling
                    - ingest_olex/ - Olex file format parser (future)
                    - ingest_maxsea/ - MaxSea file format parser (future)
                    - trips/       - Trips and track APIs
                    - history/     - Long-term coverage and marks
                    - tow_notes/   - Text notes + log image uploads
                    - updates/     - Version and update checks
                    - ai_assist/   - AI-driven suggestions (future)
  tests/          - Unit and integration tests (to be implemented)
  migrations/     - Database migrations (Alembic or similar, to be implemented)
```

## API and Data Model

- **API Specification**: For detailed endpoints and request/response shapes, see `docs/api_spec.md`
- **Database Schema**: For database tables and relationships, see `docs/db_schema.md`
- **Multi-Plotter Architecture**: For connector details (Olex Pi, MaxSea Windows), see `docs/architecture/multi_plotter_connectors.md`

## Local Development (WIP)

This section will be expanded once the initial FastAPI app is scaffolded.

**TODO:**
- Define Python version and dependency management (e.g., virtualenv/poetry)
- Add instructions to install dependencies (requirements.txt or pyproject.toml)
- Add a dev command for running the FastAPI server (e.g., `uvicorn core_api.main:app --reload`)
- Document database setup (SQLite for dev, PostgreSQL for production)
- Document how to run tests once tests are added
- Document environment variables and configuration

## Logging & Versioning

Changes to the Core API should:
- Follow the branching and versioning rules in `PROJECT_GUIDE.md`
- Be recorded in `DEVLOG.md` when substantial behavior or API contracts change
- Maintain backward compatibility for public API endpoints when possible
