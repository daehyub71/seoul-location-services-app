"""
Vercel Serverless Function Handler with Mangum adapter
"""

from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI with Mangum works!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Use Mangum adapter for serverless deployment
handler = Mangum(app)
