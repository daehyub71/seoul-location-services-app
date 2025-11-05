"""
Vercel Serverless Function Handler for FastAPI - TEST VERSION
This is a minimal test handler to verify Vercel deployment works
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create minimal FastAPI app for testing
app = FastAPI(
    title="Seoul Location Services API - Test",
    description="Minimal test deployment",
    version="0.1.0"
)

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "ok",
        "message": "Seoul Location Services API is running on Vercel!",
        "version": "0.1.0-test"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "seoul-location-services-backend",
        "environment": "production-test"
    }

# Export the FastAPI app for Vercel
handler = app
