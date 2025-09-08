"""
Search endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.aifs_client import AIFSClientManager
from app.schemas.asset import AssetSearchQuery, AssetSearchResponse, AssetSearchResult
from app.services.search_service import SearchService

router = APIRouter()


def get_search_service(
    db: Session = Depends(get_db),
    aifs_manager: AIFSClientManager = Depends(lambda: AIFSClientManager())
) -> SearchService:
    """Get search service instance."""
    return SearchService(db, aifs_manager)


@router.post("/", response_model=AssetSearchResponse)
async def search_assets(
    search_query: AssetSearchQuery,
    search_service: SearchService = Depends(get_search_service)
):
    """Search assets using vector similarity and text search."""
    try:
        results = await search_service.search(
            query=search_query.query,
            filters=search_query.filters,
            sort=search_query.sort,
            order=search_query.order,
            page=search_query.page,
            per_page=search_query.per_page,
            include_embeddings=search_query.include_embeddings
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1),
    search_service: SearchService = Depends(get_search_service)
):
    """Get search suggestions based on query."""
    try:
        suggestions = await search_service.get_suggestions(q)
        return {
            "suggestions": suggestions,
            "categories": {
                "assets": suggestions[:5],  # Top 5 asset suggestions
                "tags": [],  # TODO: Implement tag suggestions
                "content": []  # TODO: Implement content suggestions
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector")
async def vector_search(
    query: str = Query(..., min_length=1),
    k: int = Query(10, ge=1, le=100),
    filters: Optional[str] = Query(None),
    search_service: SearchService = Depends(get_search_service)
):
    """Perform vector similarity search."""
    try:
        # Parse filters if provided
        filter_dict = {}
        if filters:
            # Simple key=value parsing
            for pair in filters.split(","):
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    filter_dict[key] = value
        
        results = await search_service.vector_search(
            query=query,
            k=k,
            filters=filter_dict
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
