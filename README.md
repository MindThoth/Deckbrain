# DeckBrain

DeckBrain is a modular data intelligence platform for commercial fishing vessels. It pairs a Raspberry Pi connector that buffers Olex exports with a FastAPI backend and a map-focused Next.js dashboard so captains and owners can replay trips, track history, and keep tow notes (with photos) safely in the cloud. Future releases will layer in AI assistance for planning and risk avoidance.

## Start Here

- Read `DECKBRAIN_FOUNDATION.md` for the full vision, architecture, module pattern, and roadmap.
- Then read `PROJECT_GUIDE.md` for contribution rules, branching, and how to log changes.

## Documentation Map

- Vision and architecture: `DECKBRAIN_FOUNDATION.md`
- Workflow and branching: `PROJECT_GUIDE.md`
- Detailed docs: `docs/` (architecture/, development/, product/)

## Components (snapshot)

- Raspberry Pi connector: offline-first file queueing and upload, heartbeats, update checks.
- Core API (FastAPI): device auth, file ingestion, trips/history/tow notes endpoints.
- Dashboard (Next.js): map UI for trips, history, live status, notes, and future AI Assist.
