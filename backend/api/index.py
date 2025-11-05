"""
Vercel Serverless Function Handler

Uses simplified FastAPI app without LangGraph for fast serverless cold starts.
The full LangGraph-based API is available when running locally with uvicorn.
"""

# Import the simple serverless-optimized app
from api.simple_app import app

# Vercel will use this 'app' variable for ASGI handling
__all__ = ["app"]
