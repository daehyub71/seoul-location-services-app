"""
Vercel Serverless Function Handler
Vercel expects either:
1. A 'handler' class inheriting from BaseHTTPRequestHandler
2. An 'app' variable for ASGI/WSGI frameworks (Flask, FastAPI, etc.)
"""

from fastapi import FastAPI

# Vercel will automatically detect and use this ASGI app
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI on Vercel works!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/test")
def test():
    return {"message": "Test endpoint working"}
