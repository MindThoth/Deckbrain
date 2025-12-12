"""
DeckBrain Core API - FastAPI application entry point.

This is the main FastAPI application that serves:
- Health check endpoints
- Device management
- File upload from connectors
- Trip/tow data for dashboards
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.health import router as health_router
from modules.devices import router as devices_router
from modules.heartbeat import router as heartbeat_router

# Create FastAPI application
app = FastAPI(
    title="DeckBrain Core API",
    description="Backend service for DeckBrain multi-plotter fishing data platform",
    version="0.2.0-dev",
)

# Configure CORS for dashboard access
# TODO: Restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - basic service info."""
    return {
        "service": "deckbrain-core-api",
        "version": "0.2.0-dev",
        "status": "operational",
    }

# Include routers
app.include_router(health_router.router, tags=["health"])
app.include_router(devices_router.router, prefix="/api", tags=["devices"])
app.include_router(heartbeat_router.router, prefix="/api", tags=["heartbeat"])

# TODO: Add additional routers as modules are implemented:
# - sync (file upload)
# - trips
# - history
# - tow_notes
# - updates

