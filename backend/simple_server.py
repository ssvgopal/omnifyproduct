#!/usr/bin/env python3
"""
Simple health check server for Omnify Cloud Connect
This demonstrates the backend is working while we resolve MongoDB and dependency issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

app = FastAPI(title="Omnify Cloud Connect - Health Check", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Omnify Cloud Connect Backend",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "Backend server is operational"
    }

@app.get("/api/health")
async def api_health():
    return {
        "status": "healthy",
        "database": "not_configured",
        "message": "MongoDB connection needs to be configured"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Starting simple health check server on port {port}...")
    uvicorn.run(app, host="localhost", port=port, log_level="info")
