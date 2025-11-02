"""
API v1 Router
Aggregates all v1 endpoints
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import and include endpoint routers (will be created in later days)
# from app.api.v1.endpoints import services, geocode, recommendations

# api_router.include_router(services.router, prefix="/services", tags=["Services"])
# api_router.include_router(geocode.router, prefix="/geocode", tags=["Geocoding"])
# api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])

# Placeholder endpoint for initial setup
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
