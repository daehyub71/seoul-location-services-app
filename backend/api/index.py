"""
Vercel Serverless Function Handler

Imports the main FastAPI app from app/main.py
Vercel will automatically detect and use this ASGI app
"""

import os
import sys
import traceback

# Debug: Print Python path and environment for troubleshooting
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Python path: {sys.path}", file=sys.stderr)
print(f"Environment check:", file=sys.stderr)
print(f"  SUPABASE_URL: {'✓ Set' if os.getenv('SUPABASE_URL') else '✗ Missing'}", file=sys.stderr)
print(f"  SUPABASE_KEY: {'✓ Set' if os.getenv('SUPABASE_KEY') else '✗ Missing'}", file=sys.stderr)
print(f"  UPSTASH_URL: {'✓ Set' if os.getenv('UPSTASH_URL') else '✗ Missing'}", file=sys.stderr)
print(f"  SEOUL_API_KEY: {'✓ Set' if os.getenv('SEOUL_API_KEY') else '✗ Missing'}", file=sys.stderr)

try:
    # Import the main FastAPI application
    from app.main import app
    print("✓ App imported successfully", file=sys.stderr)
except Exception as e:
    print(f"✗ Failed to import app: {e}", file=sys.stderr)
    print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)

    # Create a minimal fallback app
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/")
    def error_root():
        return {
            "error": "Failed to initialize main app",
            "message": str(e),
            "details": "Check environment variables in Vercel Dashboard"
        }

    @app.get("/health")
    def error_health():
        return {
            "status": "error",
            "error": str(e)
        }

# Vercel will use this 'app' variable for ASGI handling
__all__ = ["app"]
