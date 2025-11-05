"""
Vercel Serverless Function Handler for FastAPI
"""

from app.main import app

# Export the FastAPI app for Vercel
# Vercel will automatically handle the ASGI interface
handler = app
