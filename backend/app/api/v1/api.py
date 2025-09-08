"""
API v1 router configuration.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import assets, conversations, search, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
