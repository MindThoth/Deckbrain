# DeckBrain Architecture Overview

DeckBrain is a modular, multi-service platform for commercial fishing vessels.  
It is built around a core + modules architecture across three systems:

----------------------------------------------------
## 1. System Overview

### Raspberry Pi Connector
- Python service running on a dedicated Raspberry Pi.
- Reads exported Olex data.
- Queues files locally using SQLite.
- Uploads files when online.
- Sends heartbeat status.
- Checks for cloud updates.

### Core API (FastAPI)
- Central backend for all vessels.
- Receives file uploads.
- Stores data under storage/<device_id>.
- Tracks device status and sync health.
- Serves trip, history, and note data.
- Stores tow notes (typed and image-based).
- Will host AI Assist logic in future versions.

### Next.js Dashboard
- Map-based interface for captains and owners.
- Features:
  - Trips view with track playback
  - History view (productive areas, marks, zones)
  - Live connector status
  - Catch notes (typed or photo-uploaded)
  - AI Assist (future)

### Future iOS App
- Will connect to the same API endpoints.
- Will support:
  - trip replay
  - catch notes
  - account management
  - offline caching

----------------------------------------------------
## 2. Data Flow Diagram

[ Olex ]  
    ↓ (exports files)  
[ Raspberry Pi Connector ]  
    - watches folders  
    - queues files  
    - uploads when online  
    - sends heartbeats  
    ↓  
[ Core API (FastAPI) ]  
    - stores files  
    - builds trips  
    - stores notes  
    - provides JSON endpoints  
    ↓  
[ Dashboard (Next.js) ]  
    - renders map  
    - displays trips & notes  
    - history overlays  
    ↓  
[ Future iOS App ]  
    - uses same endpoints  
    - mobile-friendly UI  

----------------------------------------------------
## 3. Module Pattern

Each component uses:
core/  
modules/

core/ contains:
- shared utilities  
- configuration  
- logging  
- database initialization  

modules/ contains:
- isolated features  
- each module has its own router, service, or UI layer  
- modules never import each other  

----------------------------------------------------
## 4. Scalability

The project is designed to support:
- multiple vessels  
- multiple dashboards  
- cloud scaling  
- future AI models  
- mobile clients  

----------------------------------------------------
End of architecture overview.
