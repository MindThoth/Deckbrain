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
                    - uploads/    - Upload and heartbeat handling
                    - ingestion/  - Ingestion pipeline with vendor-agnostic parser architecture
                    - trips/      - Trips and track APIs
                    - history/    - Long-term coverage and marks (future)
                    - tow_notes/  - Text notes + log image uploads (future)
                    - updates/    - Version and update checks (future)
                    - ai_assist/  - AI-driven suggestions (future)
  alembic/        - Database migrations (Alembic):
                    - versions/   - Migration files (001, 002, 003, etc.)
                    - env.py      - Alembic configuration
  scripts/        - Utility scripts (seed data, etc.)
  tests/          - Unit and integration tests (to be implemented)
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

## First-Time Setup (Required)

**Follow these steps in order for first-time setup:**

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # On Windows CMD:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   cd core-api
   pip install -r requirements.txt
   ```

3. **Run database migrations (REQUIRED):**
   ```bash
   cd core-api
   alembic upgrade head
   ```
   
   **Important:** The server will fail to start if migrations haven't been applied. This step is mandatory.

4. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API documentation (Swagger UI): `http://localhost:8000/docs`
   - Alternative documentation (ReDoc): `http://localhost:8000/redoc`

### Running the Dev Server (After Setup)

Once the database is initialized, you can start the server with:

```bash
uvicorn app.main:app --reload
```

### Current Endpoints

- `GET /` - Root endpoint with service info
- `GET /health` - Health check endpoint
- `GET /api/devices` - List all devices
- `GET /api/devices/{device_id}` - Get device details
- `POST /api/heartbeat` - Receive connector heartbeats (authentication required)
- `POST /api/upload_file` - Upload raw plotter files (authentication required)

### Authentication

All connector endpoints (`/api/heartbeat`, `/api/upload_file`) require authentication via HTTP headers:

**Required Headers:**
- `X-Device-ID`: Unique device identifier
- `X-API-Key`: API key for authentication

**Optional Headers:**
- `X-Plotter-Type`: Plotter type (olex, maxsea, etc.) - only used for auto-registration in dev mode

**Development Mode:**
- Devices are auto-created on first request with the provided API key
- API keys are hashed using SHA256 and stored securely
- Makes testing and connector development easier

**Production Mode:**
- Devices must be pre-registered before they can authenticate
- Unregistered devices receive 401 Unauthorized

**Error Responses:**
- `400 Bad Request`: Missing required headers
- `401 Unauthorized`: Invalid API key or unregistered device

### Database (Local Dev)

The Core API uses **SQLite** by default for local development (no separate database server required).

**Database Location:** `core-api/dev.db` (created automatically on first migration)

**Switching to PostgreSQL:**
1. Install PostgreSQL
2. Create a database: `createdb deckbrain`
3. Set `DATABASE_URL` environment variable:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/deckbrain"
   ```

### File Storage (Local Dev)

Uploaded files from connectors are stored locally during development.

**Storage Path Structure:**
```
storage/devices/<device_id>/raw/<yyyy>/<mm>/<dd>/<uuid>__<original_filename>
```

**Example:**
```
storage/devices/test-vessel-456/raw/2025/12/14/466145b0-6eec-46aa-8332-f6ac026f3d2a__test_track.dat
```

**Features:**
- UUID prefix prevents filename collisions
- Date-based directory structure for organization
- Storage directory created automatically on first upload
- SHA256 hash computed and stored in database for deduplication
- Files tracked in `file_records` table with metadata (file_type, source_format, processing_status)

**Processing Status Values:**
- `stored`: File stored, awaiting parsing by ingestion module
- `processed`: Successfully parsed by ingestion module
- `failed`: Parsing failed

**Resetting Dev State:**
To reset your local development database and uploaded files:
```bash
# Stop the server first
# Then delete database and storage
rm dev.db
rm -rf storage/
# Re-run migrations
alembic upgrade head
```

**Future:** In production, files will be stored in cloud object storage (S3, GCS) instead of local disk.

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

## Key Design Decisions

**Vendor-Agnostic Protocol:**
- All connector types (Olex, MaxSea, etc.) use the same upload protocol
- Vendor identification comes from `device.plotter_type` in the database, not from request bodies
- Upload endpoint works identically for all plotter types

**Authentication:**
- SHA256-based API key hashing (appropriate for long, random API keys)
- Constant-time comparison to prevent timing attacks
- Centralized in `get_authenticated_device()` dependency for reuse across endpoints

**File Storage:**
- Deterministic path structure for easy organization and cleanup
- UUID prefix ensures uniqueness while preserving original filename
- SHA256 hash stored for deduplication and integrity verification

**Development vs Production:**
- Dev mode: Auto-registration for easy testing
- Production mode: Pre-registration required for security

## What This Enables

**For Connector Development:**
- ✅ Safe, authenticated file uploads
- ✅ Consistent protocol across all plotter types (Olex, MaxSea, etc.)
- ✅ Dev-friendly auto-registration for testing
- ✅ Production-ready auth enforcement

**Next Steps:**
- Implement ingestion modules for parsing Olex and MaxSea files
- Add trips/tows data models to store normalized navigation data
- Implement Olex connector using the upload endpoint
- Implement MaxSea connector (same protocol)
- Add rate limiting to prevent abuse
- Add object storage (S3/GCS) for production file storage

## Dependencies

**Key Dependencies:**
- `fastapi`: Web framework
- `sqlalchemy`: ORM and database abstraction
- `alembic`: Database migrations
- `python-multipart`: Multipart form-data parsing for file uploads
- `passlib[bcrypt]`: API key hashing (using SHA256 implementation)

See `requirements.txt` for complete dependency list.

## Testing

### Testing Authentication and Endpoints

**1. Test Health Check (No Auth Required):**
```bash
curl http://localhost:8000/health
```

**2. Test Heartbeat with Authentication (Dev Mode - Auto-Registers Device):**
```bash
curl -X POST http://localhost:8000/api/heartbeat \
  -H "X-Device-ID: test-vessel-001" \
  -H "X-API-Key: my-secret-key-123" \
  -H "X-Plotter-Type: olex" \
  -H "Content-Type: application/json" \
  -d '{"queue_size": 5, "last_upload_ok": true, "connector_version": "1.0.0"}'
```

**3. Test File Upload:**
```bash
# Create a test file first
echo "Test plotter data" > test_file.dat

# Upload the file
curl -X POST http://localhost:8000/api/upload_file \
  -H "X-Device-ID: test-vessel-001" \
  -H "X-API-Key: my-secret-key-123" \
  -F "file=@test_file.dat" \
  -F "file_type=track" \
  -F "source_format=olex_raw"
```

**4. Test Authentication Failure (Wrong API Key):**
```bash
curl -X POST http://localhost:8000/api/heartbeat \
  -H "X-Device-ID: test-vessel-001" \
  -H "X-API-Key: wrong-key" \
  -H "Content-Type: application/json" \
  -d '{"queue_size": 0}'
```
Should return `401 Unauthorized`

**5. Test Missing Headers:**
```bash
curl -X POST http://localhost:8000/api/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"queue_size": 0}'
```
Should return `400 Bad Request` with message about missing headers

### Testing with PowerShell (Windows)

**1. Test Heartbeat:**
```powershell
$headers = @{
    'X-Device-ID' = 'test-vessel-001'
    'X-API-Key' = 'my-secret-key-123'
    'X-Plotter-Type' = 'olex'
}
$body = @{
    queue_size = 5
    last_upload_ok = $true
    connector_version = '1.0.0'
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/heartbeat `
    -Method POST `
    -Headers $headers `
    -Body $body `
    -ContentType 'application/json' `
    -UseBasicParsing
```

**2. Test File Upload:**
```powershell
$headers = @{
    'X-Device-ID' = 'test-vessel-001'
    'X-API-Key' = 'my-secret-key-123'
}

# Create test file
"Test plotter data" | Out-File -FilePath test_file.dat -Encoding utf8

# Upload file
$form = @{
    file = Get-Item test_file.dat
    file_type = 'track'
    source_format = 'olex_raw'
}

Invoke-WebRequest -Uri http://localhost:8000/api/upload_file `
    -Method POST `
    -Headers $headers `
    -Form $form `
    -UseBasicParsing
```

**3. Verify File Was Stored:**
```powershell
# Check storage directory
Get-ChildItem -Path storage -Recurse

# Check database
python -c "from core.db import SessionLocal; from core.models import FileRecord; db = SessionLocal(); records = db.query(FileRecord).all(); print(f'Found {len(records)} file records'); [print(f'  - {r.id}: {r.remote_path}, size={r.size_bytes}, sha256={r.sha256[:16]}...') for r in records]; db.close()"
```

### Using Swagger UI (Interactive Testing)

The easiest way to test is using the built-in Swagger UI:

1. Start the server: `uvicorn app.main:app --reload`
2. Open browser: `http://localhost:8000/docs`
3. Click on any endpoint to expand it
4. Click "Try it out"
5. Fill in the required headers and body
6. Click "Execute"

The Swagger UI will show you the request and response, making it easy to test all endpoints interactively.

### TODO

- Document environment variables and configuration (.env file)
- Add instructions for running tests once tests are added
- Add seed data script for local development

## Logging & Versioning

Changes to the Core API should:
- Follow the branching and versioning rules in `PROJECT_GUIDE.md`
- Be recorded in `DEVLOG.md` when substantial behavior or API contracts change
- Maintain backward compatibility for public API endpoints when possible
