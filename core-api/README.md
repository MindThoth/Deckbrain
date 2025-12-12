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

## Local Development

The Core API uses FastAPI with Uvicorn for local development.

### Prerequisites

- Python 3.10+ recommended
- Virtual environment tool (venv, virtualenv, or poetry)

### Running the Dev Server

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   cd core-api
   pip install -r requirements.txt
   ```

3. **Run the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API documentation (Swagger UI): `http://localhost:8000/docs`
   - Alternative documentation (ReDoc): `http://localhost:8000/redoc`

### Current Endpoints

- `GET /` - Root endpoint with service info
- `GET /health` - Health check endpoint
- `GET /api/devices` - List devices (placeholder)
- `GET /api/devices/{device_id}` - Get device details (placeholder)

### Database (Local Dev)

The Core API uses **SQLite** by default for local development (no separate database server required).

**Database Location:** `core-api/dev.db` (created automatically on first run)

**Switching to PostgreSQL:**
1. Install PostgreSQL
2. Create a database: `createdb deckbrain`
3. Set `DATABASE_URL` environment variable:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/deckbrain"
   ```

### Migrations (Alembic)

Database migrations are managed with Alembic.

**Apply migrations:**
```bash
cd core-api
alembic upgrade head
```

**Create a new migration (after model changes):**
```bash
alembic revision --autogenerate -m "description of changes"
```

**Rollback last migration:**
```bash
alembic downgrade -1
```

### TODO

- Document environment variables and configuration (.env file)
- Add instructions for running tests once tests are added
- Add seed data script for local development

## Logging & Versioning

Changes to the Core API should:
- Follow the branching and versioning rules in `PROJECT_GUIDE.md`
- Be recorded in `DEVLOG.md` when substantial behavior or API contracts change
- Maintain backward compatibility for public API endpoints when possible
