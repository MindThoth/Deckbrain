# DeckBrain Foundation

This document is the single source of truth for what DeckBrain is, how it works, and how it should evolve. Every AI model and human developer should read this file before making changes to the repo.

## 1. What is DeckBrain?

DeckBrain is a modular data intelligence platform for commercial fishing vessels. It connects to multiple navigation and fishing plotter systems (Olex, MaxSea TimeZero, and others) via vendor-specific connector agents, securely uploads navigation and fishing data to a cloud backend, and presents it in a map-based dashboard for captains and vessel owners. Over time, it will also provide AI-powered assistance for planning tows, avoiding bad ground, and learning from historical performance.

At a high level:
- On the boat: Vendor-specific connector agents (e.g., Olex connector on Raspberry Pi, MaxSea connector on Windows) pull plotter data and buffer it offline.
- In the cloud: Core API stores and organizes data per vessel in a plotter-agnostic format.
- For the user: Web Dashboard (and later a mobile app) shows trips, history, notes, and AI suggestions, regardless of which plotter system the vessel uses.

## 2. Vision and Goals

DeckBrain’s long-term goal is to become the “brain of the deck” for a fishing vessel:

- Never lose your plotter/ground data again (even if the machine dies or is replaced), regardless of which navigation system you use.
- Turn years of tracks, depths, and notes into something searchable and visual.
- Let captains keep old-school workflows (paper logs) while still getting a clean digital history.
- Provide a friendly, map-focused user experience that feels natural for captains.
- Eventually, offer AI tools that:
  - suggest promising areas based on past results
  - warn about “bad mud / gear risk” locations
  - highlight unexplored ground similar to places that paid off before.

The system must be:
- Offline-first on the vessel.
- Multi-boat, multi-captain capable (SaaS-style).
- Modular, so new features can be added as plugins/modules.

## 3. Users and Roles

Primary users:
- **Captain** – sees trips, history, notes, and AI assist to plan next tows.
- **Vessel Owner / Manager** – monitors boat activity, sync status, and long-term performance.
- **System Admin / Developer** – maintains the connectors, backend, and dashboard.

Future users:
- **Fleet manager** – sees multiple vessels’ performance and status.
- **Regulatory / science partner** (maybe) – access to summary views, if allowed by the owner.

## 4. High-Level Architecture

DeckBrain has three main components (with a future fourth):

1. **Connectors (Vendor-Specific Agents)**  
   - Each plotter vendor has its own connector implementation:
     - **Olex Connector**: Python service running on Raspberry Pi, watches Olex export directories.
     - **MaxSea Connector**: Python/Windows service, watches MaxSea TimeZero export/backup directories.
     - Future connectors for NavNet, WASSP, and other systems.
   - All connectors share common core functionality:
     - Queue new/changed files in a local SQLite database.
     - Upload queued files to the Core API when internet is available.
     - Send periodic heartbeats with status (queue size, last sync, version, plotter_type).
     - Check with the cloud for software update info.
   - Vendor-specific adapters handle plotter-specific file formats and directory structures.

2. **Core API (FastAPI backend)**  
   - Receives file uploads from each vessel (device_id + api_key + plotter_type).  
   - Stores raw files on disk under `storage/<device_id>/...` with source_format metadata.  
   - Tracks:
     - Devices (which boats exist, their API keys, plotter_type, and metadata)
     - File records (with source_format indicating vendor format)
     - Heartbeats (status over time, including plotter_type)
     - Tow notes (typed notes and uploaded images of log pages)  
   - Provides JSON endpoints for:
     - file upload
     - heartbeat
     - trip listings and track geojson
     - historic layers (marks, hot zones, risk zones)
     - tow notes
     - update checks
   - Designed to support many boats safely and separately, regardless of plotter vendor.
   - Uses vendor-specific ingestion modules to parse raw files into normalized DeckBrain data structures (trips, tows, soundings, marks).

3. **Dashboard (Next.js web app)**  
   - The main interface for captains and owners.  
   - Plotter-agnostic: works with data from any supported plotter system.
   - Map-centric, with tabs such as:
     - Trips – replay individual trips and tows, including track lines and depth profile.
     - Live – last sync time, last known position, queue size on the connector.
     - History – long-term ground coverage, productive zones, marks, and “avoid here” zones.
     - AI Assist – (future) area for AI-driven recommendations and warnings.
     - Settings – boat info, device details, data export options, access control.
   - May display plotter brand as metadata (e.g., "source: Olex" or "source: MaxSea") but operates on normalized data structures.
   - Provides an intuitive user experience with marine charts and overlays.

4. **Future: Mobile App (iOS / others)**  
   - A native or cross-platform app (SwiftUI or React Native/Expo) for:
     - quick trip review
     - catch notes entry
     - notifications (sync issues, new data available)
   - The mobile app will talk to the same Core API as the web dashboard.

## 5. Data Flow (End-to-End)

Basic flow (works identically for all plotter vendors):
1. **Plotter System** (Olex, MaxSea, etc.) exports navigation/fishing data to a file directory.
2. **Vendor-Specific Connector**:
   - Watches the plotter-specific export directory.
   - Detects new or modified files.
   - Stores them in a local queue (SQLite) with status = pending.
3. When internet is available:
   - Connector sends pending files to the Core API (`/api/upload_file`) with plotter_type metadata.
   - On successful response, marks them as uploaded in its local DB.
4. Connector also sends **heartbeats** (`/api/heartbeat`) indicating:
   - queue size
   - local version (from version.json)
   - plotter_type
   - last sync status (ok/error)
5. **Core API**:
   - Validates device auth (device_id, api_key).
   - Saves uploaded files under `storage/<device_id>/...` with source_format metadata.
   - Records FileRecord and Heartbeat entries in the DB (including plotter_type).
   - Routes files to vendor-specific ingestion modules (e.g., `ingest_olex`, `ingest_maxsea`) that parse raw formats into normalized DeckBrain objects.
   - Exposes derived data as:
     - trips for a device (normalized across all plotters)
     - track data per trip
     - historical coverage
     - tow notes for a given tow/trip.
6. **Dashboard**:
   - Calls Core API to:
     - list trips for a device
     - fetch track and depth data
     - fetch history layers
     - fetch tow notes
   - Renders the information on a marine-style map with side panels, regardless of source plotter.

Future data flow additions:
- AI pipeline that consumes trips, notes, and history to generate “suggested areas” and warnings.
- OCR for handwritten log images uploaded as tow notes.

## 6. Component Responsibilities (More Detail)

### 6.1 Connectors (Vendor-Specific Agents)

Main responsibilities (shared across all connector implementations):
- Offline-first handling: always safe to run with no internet.
- Reliable queueing of files to avoid data loss.
- Efficient uploads when connectivity is available.
- Sending heartbeats regularly (including plotter_type).
- Checking for updates (and eventually downloading/applying them).

Vendor-specific responsibilities:
- Olex connector: watches Olex export directories on Raspberry Pi/Linux.
- MaxSea connector: watches MaxSea TimeZero export/backup directories on Windows.
- Future connectors: adapt to their respective plotter file formats and directory structures.

Key behaviors:
- If no network: do not crash, just keep queueing.
- If server is unreachable: retry later (backoff).
- Must never delete raw plotter data without explicit design.
- All connectors use the same upload protocol and data model when talking to Core API.

### 6.2 Core API (FastAPI)

Main responsibilities:
- Device authentication and authorization (plotter-agnostic).
- File ingestion and storage (with source_format tracking).
- Vendor-specific ingestion modules that parse raw plotter files into normalized DeckBrain structures:
  - `ingest_olex`: interprets Olex file formats
  - `ingest_maxsea`: interprets MaxSea TimeZero formats
  - Future: `ingest_navnet`, `ingest_wassp`, etc.
- Building higher-level concepts (normalized across all plotters):
  - trips (grouping track segments)
  - tows (subsections of a trip)
- Managing tow notes (both text and images).
- Surfacing data for:
  - Trips view
  - History view
  - Live status view
- Providing stable, versionable JSON contracts for clients (dashboard, mobile), independent of source plotter.

### 6.3 Dashboard (Next.js)

Main responsibilities:
- Present complex data in a simple, friendly way for captains.
- Provide:
  - a big map view
  - an intuitive sidebar (trip selectors, layer toggles, notes)
  - clear status indicators (last sync, queue, version).
- Capture new information from the user:
  - typed tow notes
  - uploaded photos of handwritten log pages
- Prepare the UI for future AI features:
  - AI Assist tab
  - Visual overlays for AI-suggested zones and warnings.

### 6.4 Future Mobile App

Main responsibilities:
- Provide quick access, not full-blown analysis.
- Integrate with camera for log photo capture.
- Support push notifications from the Core API.

## 7. Module System (Core + Modules Pattern)

To keep DeckBrain maintainable, each part of the system uses a core + modules layout.

### 7.1 Connectors

**Shared Core** (`connector/shared/`):
  - config (device_id, api_key, base URL, plotter_type)
  - queue DB helper
  - HTTP client
  - logging helpers
  - version reader (version.json)
  - common upload protocol implementation

**Vendor-Specific Adapters**:
- `connector/olex_pi/`
  - watches Olex export directories (Linux/Pi)
  - vendor-specific file detection and parsing
  - uses shared core for queueing and upload
- `connector/maxsea_win/`
  - watches MaxSea TimeZero export/backup directories (Windows)
  - vendor-specific file detection and parsing
  - uses shared core for queueing and upload
- Future: `connector/navnet/`, `connector/wassp/`, etc.

**Shared Modules** (`connector/shared/modules/`):
  - `file_sync/` – generic file watching and queueing (used by all adapters)
  - `heartbeat/` – sends heartbeats with queue size, version, plotter_type, last_sync_ok
  - `updates/` – checks `/api/check_update` to see if a new connector version is available
  - future modules: `sensors/`, etc.

### 7.2 Core API

- `core-api/core/`
  - settings / configuration
  - database initialization (SQLAlchemy, migrations)
  - security helpers (verify device_id + api_key)
  - common utilities (timestamps, path builders)
- `core-api/modules/`
  - `devices/` – device registration, API key management, plotter_type tracking, summary endpoints
  - `sync/` – upload and heartbeat handling (plotter-agnostic)
  - `ingest_olex/` – parses Olex files into normalized trips/tows/soundings
  - `ingest_maxsea/` – parses MaxSea files into normalized trips/tows/soundings
  - Future: `ingest_navnet/`, `ingest_wassp/`, etc.
  - `trips/` – trips and track APIs (normalized data, plotter-agnostic)
  - `history/` – long-term coverage and marks
  - `tow_notes/` – text notes + log image uploads
  - `updates/` – version and update checks
  - `ai_assist/` (future) – AI-driven suggestions and warnings

### 7.3 Dashboard

- `dashboard/core/`
  - global layout (top nav, layout shell)
  - API client utilities
  - shared map wrapper components
  - shared styling and theme
- `dashboard/features/`
  - `trips/`
    - main trips page
    - trip selection sidebar
    - map overlays for track and notes
  - `live/`
    - last sync status, last position, connector health
  - `history/`
    - historic zones, marks, coverage
  - `ai-assist/`
    - placeholder now; later: suggestions UI
  - `settings/`
    - boat name, device details, data export, access control

### 7.4 Module Rules

- Modules may import from `core/`, but must not import from each other.
- Cross-cutting behaviors are exposed via core helpers or API calls, not direct imports.
- Adding a feature = adding a new module (or extending an existing one), not hacking logic into an unrelated file.

## 8. Offline and Sync Behavior

Key principles:
- The connector must assume that connectivity is unreliable.
- Upload logic must be:
  - idempotent
  - retriable
  - safe against duplication
- Queued files must not be lost if the connector restarts.
- The Core API must treat each upload as a potentially delayed event (accept out-of-order timestamps).
- Dashboard should show:
  - whether data is fresh (recent heartbeat)
  - how many files are pending on the vessel (from heartbeat info)
  - last successful sync time.

## 9. Catch Notes and Paper Log Photos

One of DeckBrain’s key features is helping “old-school” captains keep using their paper logbooks while still getting digital benefits.

Planned behavior:
- Captain can:
  - enter a text note for a tow/trip (e.g., “good scallop first 20 min, rocky later”)
  - upload a photo of a paper log page with times, depths, catch comments
- Core API:
  - stores raw text and/or image in TowNote records
  - later runs OCR + NLP (future) to extract structured info like:
    - good/bad
    - bottom type
    - catch quality
    - species, if present
- Dashboard:
  - shows notes pinned to tows/tracks
  - lets the user click a tow and see the notes and any attached images.

This is a strategic feature: it bridges traditional workflows with modern data usage.

## 10. AI and Future Features

AI is a later phase, but the architecture should prepare for it.

Future AI capabilities:
- AI Assist tab on dashboard:
  - Suggest likely productive areas based on:
    - past catches
    - depths
    - bottom type
    - season/time
    - patterns in notes
  - Warn about:
    - previously bad ground
    - gear-risk zones
- Automatic extraction of tags from tow notes (e.g., “good”, “muddy”, “gear damage”).
- Pattern analysis over seasons and years.

Architecture requirements:
- Stable data contracts (so models can safely query the data).
- Clean separation between:
  - data ingestion
  - data modeling
  - AI inference.

## 11. Roadmap (High Level)

Rough development roadmap (can be adjusted as needed):
- **v0.1 – Project Skeleton**
  - Repo structure
  - Documentation (this foundation, guidelines, devlog)
- **v0.2 – Trips Vertical Slice**
  - Basic connector file_sync module (local simulation)
  - Core API mock trips endpoints
  - Dashboard Trips tab with static map and fake tracks
- **v0.3 – Tow Notes + Image Upload**
  - Core API tow_notes module with text + image support
  - Dashboard Catch Notes panel with text and image upload UI
- **v0.4 – History Module**
  - Core API history module for marks and hot zones
  - Dashboard History tab with layers and toggles
- **v0.5 – AI Assist (Placeholder)**
  - Dashboard AI Assist tab with placeholder UX
  - Core API ai_assist module skeleton
- **Future**
  - OCR for handwritten logs
  - Real AI Assist using past performance
  - Fleet-level views
  - Native iOS app
  - Better offline dashboard / sync

## 12. How AI Models Should Work with This Repo

Any AI model (Copilot, Cursor, Claude, ChatGPT, etc.) that edits this repo should:
1. Read this file (`DECKBRAIN_FOUNDATION.md`) to understand the big picture.
2. Read `PROJECT_GUIDE.md` for rules on branching, commits, and module boundaries. For detailed information on how we use branches, versions, DEVLOG.md, and CHANGELOG.md, please see PROJECT_GUIDE.md.
3. Check the latest entries in `DEVLOG.md` to see what recently changed.
4. Respect the core + modules architecture:
   - don't tangle modules
   - don't bypass core helpers.
5. After making changes:
   - log them in `DEVLOG.md` (date, version tag, model, summary).
   - keep the code style consistent with existing files.

This keeps DeckBrain clean, understandable, and safe to evolve.

## 13. Multi-Plotter Support

DeckBrain is designed from the ground up to support multiple navigation and fishing plotter systems. Olex is the first supported vendor, but the architecture accommodates MaxSea TimeZero, NavNet, WASSP, and other systems.

**Key Design Principles:**
- Each plotter vendor has its own connector agent (e.g., `connector/olex_pi`, `connector/maxsea_win`).
- All connectors share a common core (`connector/shared/`) for queueing, HTTP, heartbeats, and updates.
- Vendor-specific adapters handle plotter-specific file formats and directory structures.
- The Core API stores data in a normalized format (trips, tows, notes, file_records) with metadata fields (`plotter_type`, `source_format`) indicating the source system.
- Vendor-specific ingestion modules (`core-api/modules/ingest_olex`, `ingest_maxsea`, etc.) convert raw files into normalized DeckBrain objects.
- The Dashboard is plotter-agnostic and works with normalized data from any supported plotter.

For detailed information on the connector architecture and how different plotters integrate, see `docs/architecture/multi_plotter_connectors.md`.

## 14. Where to Find More Docs

- Architecture details: `docs/architecture/overview.md`, `docs/architecture/modules.md`, `docs/architecture/multi_plotter_connectors.md`
- Development practices: `docs/development/environment_setup.md`, `docs/development/testing_strategy.md`
- Product roadmap: `docs/product/feature_roadmap.md`

End of DECKBRAIN_FOUNDATION.md

