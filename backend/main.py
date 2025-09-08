"""
AIFS Client Backend - FastAPI application
Main entry point for the AIFS client backend service.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.database import init_db
from app.core.aifs_client import AIFSClientManager
from app.api.v1.api import api_router
from app.core.exceptions import AIFSException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AIFS Client Backend...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize AIFS client
    try:
        aifs_manager = AIFSClientManager()
        await aifs_manager.initialize()
        app.state.aifs_manager = aifs_manager
        logger.info("AIFS client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize AIFS client: {e}")
        # Continue without AIFS for development
    
    yield
    
    # Shutdown
    logger.info("Shutting down AIFS Client Backend...")
    if hasattr(app.state, 'aifs_manager'):
        await app.state.aifs_manager.close()


# Create FastAPI application
app = FastAPI(
    title="AIFS Client API",
    description="AI-Native File System Client with RAG capabilities",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# Global exception handler
@app.exception_handler(AIFSException)
async def aifs_exception_handler(request, exc: AIFSException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "details": str(exc) if settings.ENVIRONMENT == "development" else None
            }
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AIFS Client API",
        "version": "1.0.0",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
