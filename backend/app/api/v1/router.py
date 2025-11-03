"""
API v1 Router
Aggregates all v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import services, geocode

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(services.router, tags=["Services"])
api_router.include_router(geocode.router, tags=["Geocoding"])

# Status endpoint
@api_router.get("/status")
async def api_status():
    """
    API status endpoint
    """
    return {
        "status": "operational",
        "version": "v1",
        "message": "Seoul Location Services API is ready"
    }
