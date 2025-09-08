"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from app.core.aifs_client import AIFSClientManager
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "aifs-client-api",
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check(
    db: Session = Depends(get_db),
    aifs_manager: AIFSClientManager = Depends(lambda: AIFSClientManager())
):
    """Detailed health check including dependencies."""
    health_status = {
        "status": "healthy",
        "service": "aifs-client-api",
        "version": "1.0.0",
        "checks": {
            "database": "healthy",
            "aifs_server": "unknown"
        }
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check AIFS server
    try:
        if aifs_manager.is_connected:
            health_status["checks"]["aifs_server"] = "healthy"
        else:
            health_status["checks"]["aifs_server"] = "disconnected"
    except Exception as e:
        health_status["checks"]["aifs_server"] = f"unhealthy: {str(e)}"
    
    return health_status
