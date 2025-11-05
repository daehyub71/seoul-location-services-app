"""
Simple FastAPI Application for Vercel Serverless
Without LangGraph/heavy dependencies for fast cold starts
"""

import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """
    Search nearby services

    Note: This is a placeholder endpoint for serverless deployment.
    Full functionality requires database connection which will be added
    after environment configuration is complete.
    """

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

    # Return mock data for now
    return {
        "query": {
            "location": {"lat": lat, "lon": lon},
            "radius": radius,
            "category": category,
            "limit": limit
        },
        "summary": {
            "total_found": 0,
            "returned": 0,
            "categories": {}
        },
        "services": [],
        "message": "Database connection will be configured after deployment verification.",
        "status": "placeholder"
    }


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
