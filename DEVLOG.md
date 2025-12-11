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