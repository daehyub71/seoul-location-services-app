"""
Vercel Serverless Function Handler

Imports the main FastAPI app from app/main.py
Vercel will automatically detect and use this ASGI app
"""

import os
import sys
import traceback
from fastapi import FastAPI

# Create diagnostic app first
app = FastAPI(title="Seoul Location Services API")

@app.get("/")
def root():
    """Root endpoint with environment diagnostics"""
    env_vars = {
        "SUPABASE_URL": "✓ Set" if os.getenv('SUPABASE_URL') else "✗ Missing",
        "SUPABASE_KEY": "✓ Set" if os.getenv('SUPABASE_KEY') else "✗ Missing",
        "SUPABASE_SERVICE_ROLE_KEY": "✓ Set" if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else "✗ Missing",
        "SUPABASE_DATABASE_URL": "✓ Set" if os.getenv('SUPABASE_DATABASE_URL') else "✗ Missing",
        "UPSTASH_URL": "✓ Set" if os.getenv('UPSTASH_URL') else "✗ Missing",
        "UPSTASH_TOKEN": "✓ Set" if os.getenv('UPSTASH_TOKEN') else "✗ Missing",
        "SEOUL_API_KEY": "✓ Set" if os.getenv('SEOUL_API_KEY') else "✗ Missing",
    }

    missing_vars = [k for k, v in env_vars.items() if "Missing" in v]

    return {
        "message": "Seoul Location Services API - Environment Check",
        "python_version": sys.version,
        "environment_variables": env_vars,
        "status": "OK" if not missing_vars else "Missing Required Variables",
        "missing": missing_vars if missing_vars else None
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running"
    }

@app.get("/env-test")
def env_test():
    """Detailed environment test"""
    return {
        "all_env_vars": list(os.environ.keys()),
        "supabase_url_value": os.getenv('SUPABASE_URL', 'NOT_SET')[:50] if os.getenv('SUPABASE_URL') else 'NOT_SET'
    }

# Try to import and replace with main app if environment is ready
try:
    missing_required = []
    required_vars = [
        'SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_SERVICE_ROLE_KEY',
        'SUPABASE_DATABASE_URL', 'UPSTASH_URL', 'UPSTASH_TOKEN', 'SEOUL_API_KEY'
    ]

    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)

    if missing_required:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_required)}")

    # All required vars present, import main app
    from app.main import app as main_app
    app = main_app
    print("✓ Main app loaded successfully", file=sys.stderr)

except Exception as e:
    print(f"✗ Using diagnostic app instead of main app: {e}", file=sys.stderr)
    # Keep using the diagnostic app defined above

# Vercel will use this 'app' variable for ASGI handling
__all__ = ["app"]
