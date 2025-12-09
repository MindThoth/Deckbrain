# DeckBrain Modules Documentation

This document explains the module structure for every part of the system.

----------------------------------------------------
## 1. Philosophy

Modules = isolated features that plug into a stable core.  
Core = shared utilities that never depend on modules.  
Modules may import from core, but never from each other.

----------------------------------------------------
## 2. Connector Modules (Raspberry Pi)

Located in `connector/modules/`

Examples:
- file_sync  
- heartbeat  
- updates  

Each module contains:
- service logic  
- optional helpers  

----------------------------------------------------
## 3. Core API Modules (FastAPI)

Located in `core-api/modules/`

Examples:
- devices  
- sync  
- trips  
- history  
- tow_notes  
- updates  
- ai_assist (future)  

Each module has:
- router.py  
- service.py  
- models.py (if needed)  

----------------------------------------------------
## 4. Dashboard Feature Modules (Next.js)

Located in `dashboard/features/`

Examples:
- trips  
- live  
- history  
- ai-assist  
- settings  

Each module contains:
- page component  
- sidebar components  
- map overlays  
- hooks/utilities  

----------------------------------------------------
## 5. Adding a New Module

Steps:
1. Create module folder in connector/modules, core-api/modules, or dashboard/features.  
2. Add minimal router/service/UI.  
3. Document in DEVLOG.md.  
4. Update docs/roadmap.md if it is a planned feature.  

Modules must NOT import each other.

----------------------------------------------------
End of modules documentation.
