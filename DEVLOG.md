# DeckBrain Development Log
A chronological log of day-by-day development changes.  
Every update (by humans or AI) must be recorded.

### 2025-12-09 – v0.1.0-dev
- Initialized project skeleton (docs + folders).
- Added README.md, PROJECT_GUIDE.md, CHANGELOG.md, DEVLOG.md.
- Added docs: architecture.md, modules.md, roadmap.md.
- Created connector/core, connector/modules, core-api/core, core-api/modules, dashboard/app, dashboard/core, dashboard/features.
- Added empty LICENSE and .gitignore.

(When making changes, append new entries below this entry with:)
- Date  
- Version increment  
- Model used  
- Summary of modifications  

### 2025-12-10 – v0.1.1-docs
- Added `DECKBRAIN_FOUNDATION.md` as the single source for vision, architecture, modules, roadmap, and AI/human rules; merged prior doc details.
- Shortened `README.md` and refocused `PROJECT_GUIDE.md` to point to the foundation and emphasize workflow.
- Removed superseded docs (`docs/architecture.md`, `docs/modules.md`, `docs/roadmap.md`) to avoid fragmentation.
- Model: gpt-5.1-codex-max-low.

### 2025-12-10 – v0.1.1-dev – branch: main
- Model: Cursor (with GPT-based assistant)
- Changes:
  - Added a "Versioning, Branches, and Logs" section to PROJECT_GUIDE.md.
  - Linked DECKBRAIN_FOUNDATION.md to PROJECT_GUIDE.md for workflow details.
- Notes:
  - This entry tests and documents the new logging and branching process.

### 2025-12-11 – v0.1.1-dev – branch: main
- Model: Cursor (with GPT-based assistant)
- Changes:
  - Organized documentation into docs/architecture, docs/development, and docs/product.
  - Normalized or moved existing docs into the new structure.
  - Ensured root contains only core summary docs (README, DECKBRAIN_FOUNDATION, PROJECT_GUIDE, DEVLOG, CHANGELOG).
  - Created code service folders (connector, core-api, dashboard, mobile, scripts) with short README files to mark them as code zones.
- Notes:
  - This reorganization establishes a professional structure where all runtime code lives under service folders and all secondary docs live under docs/.

### 2025-12-11 – v0.1.2-dev – branch: main
- Model: Cursor (with GPT-based assistant)
- Changes:
  - Updated DECKBRAIN_FOUNDATION.md to clarify that DeckBrain is a multi-plotter platform, with Olex as the first supported vendor.
  - Added docs/architecture/multi_plotter_connectors.md describing vendor-specific connectors and the shared upload protocol.
  - Tweaked architecture docs (docs/architecture/overview.md, docs/architecture/modules.md) to avoid implying Olex-only support and to mention future MaxSea integration.
- Notes:
  - This documents the intention to support Olex, MaxSea, and other plotters via separate connector agents feeding a shared Core API. The Dashboard remains plotter-agnostic and works with normalized data from any supported system.

### 2025-12-11 – v0.1.3-dev – branch: main
- Model: Cursor (with GPT-based assistant)
- Changes:
  - Defined multi-plotter connector architecture for Olex (Raspberry Pi) and MaxSea TimeZero (Windows).
  - Added docs/architecture/multi_plotter_connectors.md describing shared connector core and vendor-specific agents.
  - Updated DECKBRAIN_FOUNDATION.md, docs/db_schema.md, and docs/api_spec.md to reflect multi-plotter support using plotter_type and source_format.
  - Created connector/shared, connector/olex_pi, and connector/maxsea_win directories with README files to mark their roles.
- Notes:
  - This establishes Option A: one shared connector core with vendor-specific connectors for Olex and MaxSea, all using the same Core API protocol.

### 2025-12-11 – v0.1.4-dev – branch: main
- Model: Cursor (with GPT-based assistant)
- Changes:
  - Expanded core-api/README.md into a full service README describing responsibilities, structure, and links to API/schema docs.
- Notes:
  - This makes the Core API easier to understand in isolation and clarifies where to find API and database documentation.

### 2025-12-11 – v0.1.5-dev – branch: main
- Model: Cursor (with GPT-based assistant)
- Changes:
  - Added commit/logging/branching guidelines under docs/engineering/commit_and_log_guidelines.md.
  - Updated PROJECT_GUIDE.md to reference the new guideline.
- Notes:
  - This document formalizes how contributors and AI tools should structure commits, DEVLOG entries, and CHANGELOG updates.

### 2025-12-12 – v0.2.0-dev – branch: main
- Model: Cursor (with Claude Sonnet 4.5)
- Changes:
  - Created initial FastAPI skeleton for core-api with app/main.py, core/config.py, core/db.py, and basic modules for health and devices.
  - Added minimal requirements.txt with FastAPI, Uvicorn, and Pydantic dependencies.
  - Updated core-api/README.md with runnable dev server instructions.
  - Documented /health and placeholder /api/devices endpoints in docs/api_spec.md.
- Notes:
  - This marks the start of v0.2.0-dev (Trips vertical slice) by first establishing a runnable Core API shell.
  - The app is now runnable with: cd core-api && uvicorn app.main:app --reload
  - Placeholder endpoints return mock data; database integration is next.

### 2025-12-12 – v0.2.1-dev – branch: main
- Model: Cursor (with GPT-based assistant)
- Changes:
  - Added SQLAlchemy + Alembic database layer to core-api, using SQLite by default for local development.
  - Implemented initial models: Device, Heartbeat, FileRecord with proper relationships and indexes.
  - Added first Alembic migration (001) to create core tables: devices, heartbeats, file_records.
  - Implemented DB-backed endpoints: GET /api/devices, GET /api/devices/{device_id}, POST /api/heartbeat.
  - Updated core-api/README.md with database setup and Alembic migration instructions.
  - Updated docs/api_spec.md and docs/db_schema.md to match the implementation.
- Notes:
  - Authentication enforcement is intentionally deferred; current goal is to validate end-to-end ingestion and persistence.
  - Database migrations can be applied with: cd core-api && alembic upgrade head
  - PostgreSQL support is ready via DATABASE_URL environment variable.

### 2025-12-13 – v0.2.2-dev – branch: main
- Model: Cursor (with GPT-based assistant)
- Changes:
  - Added database initialization sanity checks to fail fast when migrations are missing.
  - Added startup event in app/main.py that verifies 'devices' table exists before server starts.
  - Improved heartbeat endpoint error handling to catch missing table errors and return developer-friendly messages.
  - Clarified first-time setup steps in core-api README with explicit migration requirement.
- Notes:
  - Prevents confusing 500 errors caused by uninitialized SQLite databases.
  - Server now fails immediately on startup with clear error message if migrations haven't been applied.

### 2025-12-13 – v0.2.3-dev – branch: main
- Model: Cursor (with Sonnet 4.5)
- Changes:
  - Enforced device API key authentication for all connector endpoints (heartbeat, upload_file).
  - Added core/auth.py with bcrypt-based API key hashing and authentication dependency.
  - Implemented vendor-agnostic POST /api/upload_file endpoint for raw file uploads.
  - Files stored locally with deterministic path structure: storage/devices/<device_id>/raw/<yyyy>/<mm>/<dd>/<uuid>__<filename>.
  - Added sha256 hashing and file_records tracking with received_at timestamp.
  - Created Alembic migration (002) for sha256 and received_at fields in file_records.
  - Updated API spec and README with authentication requirements and storage configuration.
  - Added passlib[bcrypt] and python-multipart dependencies.
- Notes:
  - Raw ingestion only; no plotter-specific parsing yet.
  - In dev mode, devices auto-register on first request with provided API key.
  - In production mode, devices must be pre-registered.
  - Unlocks safe connector development with proper authentication.

### 2025-12-14 – v0.2.4-dev – branch: main
- Model: Cursor (Claude Sonnet 4.5)
- Changes:
  - Introduced ingestion module with vendor-agnostic parsing architecture.
  - Created modules/ingestion/ with parsers/, registry.py, service.py, and router.py.
  - Implemented BaseParser abstract interface and ParseResult dataclass.
  - Added stub parsers for Olex (OlexParser) and MaxSea (MaxSeaParser).
  - Implemented parser registry for source_format-based routing.
  - Built ingestion service orchestration (ingest_file, ingest_file_safe).
  - Added manual ingestion trigger endpoint: POST /api/ingest/{file_record_id}.
  - Added parser listing endpoint: GET /api/ingest/parsers.
  - Updated processing_status semantics: stored → processing → parsed_stub/failed.
  - Created comprehensive ingestion pipeline documentation (docs/engineering/ingestion_pipeline.md).
  - Updated db_schema.md with detailed processing_status values.
  - Registered ingestion router in app/main.py.
- Notes:
  - No real plotter parsing yet; parsers are stubs only.
  - Parsers return successful ParseResult with no entities and clear stub messages.
  - This establishes the ingestion backbone for future real parsing implementation.
  - Upload flow remains unchanged; ingestion is triggered manually via API for now.

### 2025-12-14 – v0.2.5-dev – branch: main
- Model: Cursor (Claude Sonnet 4.5)
- Changes:
  - Wired automatic ingestion into upload endpoint (dev mode only).
  - Upload endpoint now calls ingest_file_safe() after successful file storage.
  - Auto-ingestion guarded by APP_ENV="development" check.
  - Upload always succeeds even if ingestion fails (upload reliability preserved).
  - Added [AUTO-INGEST] logging prefix for clear distinction.
  - Upload response now returns final processing_status (parsed_stub or failed after ingestion).
  - Updated ingestion_pipeline.md with "Automatic Ingestion (Dev Mode)" section.
- Notes:
  - End-to-end flow now works: upload → stored → auto-ingest → parsed_stub.
  - Parsing remains stub-only (no real data extraction).
  - Ingestion runs synchronously in dev; will use background jobs in production.
  - Manual ingestion endpoint still available for testing/debugging.

### 2025-12-14 – v0.2.6-dev – branch: main
- Model: Cursor (Claude Sonnet 4.5)
- Changes:
  - Created Trip, Tow, Sounding database models (normalized across all plotter types).
  - Added Alembic migration (003) for trips, tows, soundings tables with proper indexes.
  - Updated Device model with trips and soundings relationships.
  - Built trips API module (modules/trips/) with full endpoint suite:
    - GET /api/trips - list trips with pagination
    - GET /api/trips/{trip_id} - get trip details with tows
    - GET /api/trips/{trip_id}/track - get GeoJSON track data
    - GET /api/trips/{trip_id}/tows/{tow_id}/track - get tow track data
  - Created GeoJSON utilities for converting soundings to map-ready format.
  - Created seed script (scripts/seed_mock_trips.py) for mock trip data generation.
  - Registered trips router in app/main.py.
  - Updated docs/api_spec.md with trips endpoint documentation.
- Notes:
  - Trips vertical slice (v0.2) Core API backend is complete.
  - Mock data includes 3 trips with 4 tows and ~345 soundings.
  - All trip data is normalized and plotter-agnostic.
  - Ready for dashboard integration (Next.js).
  - Real parsing will populate these tables when implemented.

### 2025-12-15 – v0.2.7-dev – branch: main
- Model: Cursor (Claude Sonnet 4.5)
- Changes:
  - Built Next.js dashboard with map-based trips visualization.
  - Created dashboard structure with core/ and features/ directories.
  - Implemented API client with TypeScript types matching Core API.
  - Built MapView component using Leaflet for track display.
  - Created TripList sidebar component with trip selection.
  - Wired trips page with sidebar + map layout.
  - Applied marine-focused styling with custom ocean/nautical Tailwind theme.
  - Added configuration system with environment variables.
  - Consolidated connector documentation (removed redundant READMEs).
- Notes:
  - v0.2 Trips Vertical Slice is now COMPLETE (Core API + Dashboard end-to-end).
  - Dashboard displays mock trip data with interactive map.
  - Map shows trip tracks as blue LineStrings, tow boundaries as orange lines.
  - Start/end markers and popups with trip details.
  - Ready for real trip data when parsing is implemented.
  - Next: v0.3 (Tow Notes) or implement real Olex/MaxSea parsing.

### 2025-12-15 – v0.2.8-dev – branch: main
- Model: Cursor (Claude Sonnet 4.5)
- Changes:
  - Added research documentation structure for Olex and MaxSea parsing preparation.
  - Created docs/research/olex/README.md with comprehensive file format checklist.
  - Created docs/research/maxsea/README.md with comprehensive file format checklist.
  - Added gitignored sample drop folders (samples/olex/, samples/maxsea/).
  - Created scripts/inspect_plotter_file.py - lightweight file inspection tool.
  - Tool inspects unknown plotter files without parsing (shows size, hash, type, structure).
  - Supports text preview, hex dump, ZIP inspection, encoding detection.
  - Updated .gitignore to exclude sample files but preserve .gitkeep markers.
- Notes:
  - This is preparatory work to accelerate real parser implementation once sample files are available.
  - No parsing logic added - parsers remain stubs.
  - Research docs provide structured checklists for analyzing Olex and MaxSea file formats.
  - Inspection tool helps quickly understand unknown file formats without manual hex editors.