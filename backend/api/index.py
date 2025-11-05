"""
Vercel Serverless Function Handler - MINIMAL FastAPI TEST
"""

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "It works!"}

handler = app
