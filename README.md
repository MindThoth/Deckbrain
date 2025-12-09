# DeckBrain

DeckBrain is a modular data intelligence platform for commercial fishing vessels. It is built around three core components:

1. **Raspberry Pi Connector (on the vessel)**  
   A Python-based offline-first service that runs on a dedicated Raspberry Pi.  
   It monitors exported Olex data (tracks, soundings, marks, bathymetry), queues files locally, and uploads them securely when internet becomes available.  
   It also sends heartbeat status updates and checks for remote software updates.

2. **Core Cloud API (FastAPI backend)**  
   A secure central backend that:  
   - Stores uploaded files per vessel (device_id)  
   - Tracks connector health, versions, and sync status  
   - Builds trips and track data for map replay  
   - Stores tow notes (typed or image-based)  
   - Serves JSON data to the dashboard and future mobile apps  

3. **Next.js Dashboard**  
   A web dashboard designed for captains and vessel owners.  
   Features include:  
   - Interactive map with marine-style layers  
   - Trip replay and tow visualization  
   - Long-term fishing ground history  
   - Catch/tow notes, including photo uploads of handwritten logs  
   - Live vessel sync status  
   - Future AI Assist tab for predictive fishing insights  

DeckBrain uses a **core + modules** architecture across all components for scalability and maintainability.

See `PROJECT_GUIDE.md` for development guidelines.
