"""
Vercel Serverless Function Handler

Imports the main FastAPI app from app/main.py
Vercel will automatically detect and use this ASGI app
"""

# Import the main FastAPI application
from app.main import app

# Vercel will use this 'app' variable for ASGI handling
__all__ = ["app"]
