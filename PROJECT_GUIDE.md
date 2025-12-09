# DeckBrain Project Guide
This document explains how to work inside the DeckBrain repository.  
It is the first file any AI model or developer should read before contributing.

----------------------------------------------------
## 1. Architecture Overview
DeckBrain consists of three major systems:

### A. Connector (Raspberry Pi)
Python-based service that:  
- Watches Olex data export directories  
- Queues files in a local SQLite database  
- Uploads files when online  
- Sends heartbeat status  
- Checks for updates  

Structure:
connector/  
  core/  
  modules/

### B. Core API (FastAPI)
Handles:  
- File uploads  
- Device tracking  
- Trip & history data  
- Tow notes (typed + image uploads)  
- Update version checks  

Structure:
core-api/  
  core/  
  modules/

### C. Dashboard (Next.js)
Provides a map-based UI with:  
- Trips  
- History  
- Live Status  
- Tow Notes  
- AI Assist (future)  

Structure:
dashboard/  
  app/  
  core/  
  features/

----------------------------------------------------
## 2. Core + Module Architecture Rules

### Rule 1 — Core is the foundation  
Each system has a `core/` folder for shared utilities:
- configuration
- logging  
- database setup  
- shared helpers  

### Rule 2 — Modules depend on core, not on each other  
Bad: history → trips  
Good: history → core  

### Rule 3 — New features = new modules  
Follow structure:
- connector/modules/<module>  
- core-api/modules/<module>  
- dashboard/features/<module>  

### Rule 4 — Log all changes in DEVLOG.md  
Every modification must record:  
- date  
- version tag  
- model used  
- summary of changes  

----------------------------------------------------
## 3. Branching Workflow

Use:  
- main → stable  
- dev → active work  
- feature/<name> → new modules/features  
- fix/<name> → bug fixes  

----------------------------------------------------
## 4. Commit Message Style

Examples:  
- feat: add trips module skeleton  
- fix: heartbeat queue bug  
- docs: update architecture guide  

----------------------------------------------------
## 5. Before Making ANY Change

An AI model MUST:  
1. Read PROJECT_GUIDE.md  
2. Read docs/architecture.md  
3. Read latest entries in DEVLOG.md  
4. Follow module boundaries  
5. Document its changes  

----------------------------------------------------
End of project guide.
