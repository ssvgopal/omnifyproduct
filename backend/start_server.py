#!/usr/bin/env python3
"""
Startup script for Omnify Cloud Connect backend server
Handles environment configuration and starts the FastAPI server
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def main():
    port = int(os.environ.get("PORT", 8000))
    
    mongo_url = os.environ.get("MONGO_URL")
    if not mongo_url:
        logger.warning("=" * 60)
        logger.warning("WARNING: MONGO_URL environment variable is not set!")
        logger.warning("The server will start but may fail when database is accessed.")
        logger.warning("Please provide a MongoDB connection string via MONGO_URL environment variable.")
        logger.warning("=" * 60)
        os.environ["MONGO_URL"] = "mongodb://localhost:27017"
    
    if not os.environ.get("JWT_SECRET_KEY"):
        logger.warning("JWT_SECRET_KEY not set, using default (not secure for production)")
        os.environ["JWT_SECRET_KEY"] = "dev-secret-key-change-in-production-12345678901234567890"
    
    if not os.environ.get("DB_NAME"):
        os.environ["DB_NAME"] = "omnify_cloud"
    
    if not os.environ.get("CORS_ORIGINS"):
        os.environ["CORS_ORIGINS"] = "*"
    
    logger.info(f"Starting Omnify Cloud Connect Backend on port {port}...")
    logger.info(f"MongoDB: {os.environ.get('MONGO_URL', 'Not configured')}")
    logger.info(f"Database: {os.environ.get('DB_NAME', 'omnify_cloud')}")
    
    uvicorn.run(
        "agentkit_server:app",
        host="127.0.0.1",
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
