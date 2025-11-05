"""
Simple FastAPI Application for Vercel Serverless
Without LangGraph/heavy dependencies for fast cold starts
"""

import os
import math
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Supabase client (lazy initialization)
_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Get or create Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")

    return _supabase_client


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula
    Returns distance in meters
    """
    R = 6371000  # Earth radius in meters

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

# Create FastAPI app
app = FastAPI(
    title="Seoul Location Services API",
    description="위치 기반 서울시 공공 서비스 정보 API (Serverless Version)",
    version="v1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8501",
    "https://seoul-location-services.vercel.app",
    "https://seoul-location-services-frontend.vercel.app",
    "https://seoul-location-services-frontend-k4mlsduzj-daehyub71s-projects.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Allow all Vercel preview deployments
    allow_origin_regex=r"https://.*\.vercel\.app",
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Seoul Location Services API - Serverless Version",
        "version": "v1",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "services": "/api/v1/services/nearby",
            "categories": "/api/v1/services/categories",
            "status": "/api/v1/status"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "v1",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "cache_enabled": os.getenv("CACHE_ENABLED", "true") == "true"
    }


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": "v1",
        "message": "Seoul Location Services API is ready",
        "features": {
            "services_search": "available",
            "geocoding": "available",
            "llm_recommendations": "disabled (serverless mode)"
        }
    }


@app.get("/api/v1/services/categories")
async def get_categories():
    """Get available service categories"""
    categories = {
        "cultural_events": {
            "name": "문화행사",
            "description": "서울시 문화행사 정보",
            "icon": "🎭"
        },
        "libraries": {
            "name": "도서관",
            "description": "공공도서관 및 장애인도서관",
            "icon": "📚"
        },
        "cultural_spaces": {
            "name": "문화공간",
            "description": "문화공간 및 시설",
            "icon": "🏛️"
        },
        "reservations": {
            "name": "공공예약",
            "description": "진료/교육/문화행사 예약",
            "icon": "📅"
        },
        "heritage": {
            "name": "서울미래유산",
            "description": "서울미래유산",
            "icon": "🏛️"
        }
    }

    return {
        "categories": categories,
        "total": len(categories)
    }


@app.get("/api/v1/services/nearby")
async def search_nearby_services(
    lat: Optional[float] = Query(None, description="위도 (WGS84)"),
    lon: Optional[float] = Query(None, description="경도 (WGS84)"),
    address: Optional[str] = Query(None, description="주소"),
    radius: int = Query(2000, ge=100, le=10000, description="검색 반경 (미터)"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(50, ge=1, le=200, description="최대 결과 개수")
):
    """Search nearby services"""

    # Validate input
    if not lat or not lon:
        if not address:
            raise HTTPException(
                status_code=400,
                detail="Either (lat, lon) or address must be provided"
            )
        else:
            raise HTTPException(
                status_code=501,
                detail="Geocoding service not yet configured. Please use lat/lon coordinates."
            )

    try:
        supabase = get_supabase()
        all_services = []
        categories_count = {}

        # Define table mappings
        table_configs = [
            {
                "name": "cultural_events",
                "category": "cultural_events",
                "label": "문화행사",
                "lat_field": "lat",
                "lon_field": "lot",
                "icon": "🎭"
            },
            {
                "name": "libraries",
                "category": "libraries",
                "label": "도서관",
                "lat_field": "latitude",
                "lon_field": "longitude",
                "icon": "📚"
            }
        ]

        # Fetch from each table
        for table in table_configs:
            # Skip if category filter doesn't match
            if category and category != table["category"]:
                continue

            # Fetch all records from table
            response = supabase.table(table["name"]).select("*").execute()

            if response.data:
                # Calculate distance and filter
                for item in response.data:
                    item_lat = item.get(table["lat_field"])
                    item_lon = item.get(table["lon_field"])

                    if item_lat and item_lon:
                        distance = calculate_distance(lat, lon, item_lat, item_lon)

                        if distance <= radius:
                            # Format service data
                            service = {
                                "id": item.get("id", item.get("api_id")),
                                "title": item.get("title") or item.get("library_name", "Unknown"),
                                "category": table["category"],
                                "category_label": table["label"],
                                "icon": table["icon"],
                                "location": {
                                    "lat": item_lat,
                                    "lon": item_lon,
                                    "distance": round(distance, 1)
                                },
                                "address": item.get("address") or item.get("place", ""),
                                "description": item.get("etc_desc") or item.get("facilities", ""),
                                "raw_data": item
                            }
                            all_services.append(service)

                            # Update category count
                            cat_key = table["category"]
                            categories_count[cat_key] = categories_count.get(cat_key, 0) + 1

        # Sort by distance
        all_services.sort(key=lambda x: x["location"]["distance"])

        # Apply limit
        all_services = all_services[:limit]

        return {
            "query": {
                "location": {"lat": lat, "lon": lon},
                "radius": radius,
                "category": category,
                "limit": limit
            },
            "summary": {
                "total_found": len(all_services),
                "returned": len(all_services),
                "categories": categories_count
            },
            "services": all_services
        }

    except Exception as e:
        logger.error(f"Error fetching services: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch services: {str(e)}"
        )


@app.get("/api/v1/geocode")
async def geocode_address(
    address: str = Query(..., description="주소 (예: 서울시청)")
):
    """
    Convert address to coordinates

    Note: This is a placeholder endpoint for serverless deployment.
    """
    raise HTTPException(
        status_code=501,
        detail="Geocoding service not yet configured."
    )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )
