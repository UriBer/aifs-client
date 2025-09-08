"""
Search service for asset search functionality.
"""

import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.core.aifs_client import AIFSClientManager
from app.core.exceptions import SearchError
from app.models.asset import Asset as AssetModel
from app.schemas.asset import AssetSearchResponse, AssetSearchResult
from app.services.asset_service import AssetService
from app.services.embedding_service import EmbeddingService

class SearchService:
    """Service for search operations."""
    
    def __init__(self, db: Session, aifs_manager: AIFSClientManager):
        self.db = db
        self.aifs_manager = aifs_manager
        self.asset_service = AssetService(db, aifs_manager)
        self.embedding_service = EmbeddingService()
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: str = "created_at",
        order: str = "desc",
        page: int = 1,
        per_page: int = 20,
        include_embeddings: bool = False
    ) -> AssetSearchResponse:
        """Search assets using vector similarity and text search."""
        start_time = time.time()
        
        try:
            # Try vector search first if embedding service is available
            if self.embedding_service.is_available():
                try:
                    return await self._vector_search(
                        query=query,
                        filters=filters,
                        sort=sort,
                        order=order,
                        page=page,
                        per_page=per_page,
                        include_embeddings=include_embeddings
                    )
                except Exception as e:
                    # Fall back to text search if vector search fails
                    print(f"Vector search failed, falling back to text search: {e}")
            
            # Fallback to text search
            return await self._text_search(
                query=query,
                filters=filters,
                sort=sort,
                order=order,
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            raise SearchError(f"Search operation failed: {e}")
        finally:
            query_time = time.time() - start_time
    
    async def _vector_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: str = "created_at",
        order: str = "desc",
        page: int = 1,
        per_page: int = 20,
        include_embeddings: bool = False
    ) -> AssetSearchResponse:
        """Perform vector similarity search."""
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_query_embedding(query)
        if not query_embedding:
            raise SearchError("Failed to generate query embedding")
        
        # Search in AIFS if connected
        if self.aifs_manager.is_connected:
            try:
                aifs_client = self.aifs_manager.get_client()
                vector_results = await aifs_client.vector_search(
                    query_embedding=query_embedding,
                    k=per_page * 2,  # Get more results for filtering
                    filter_metadata=filters
                )
                
                # Convert to search results
                search_results = []
                for result in vector_results:
                    asset = await self.asset_service.get_asset(result["asset_id"])
                    if asset:
                        search_results.append(AssetSearchResult(
                            asset=asset,
                            relevance_score=result["score"],
                            matched_fields=["content"],
                            snippet=result.get("snippet")
                        ))
                
                # Apply pagination
                total = len(search_results)
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_results = search_results[start_idx:end_idx]
                
                return AssetSearchResponse(
                    results=paginated_results,
                    total=total,
                    page=page,
                    per_page=per_page,
                    query_time=time.time() - time.time(),  # Will be set by caller
                    suggestions=[]
                )
                
            except Exception as e:
                raise SearchError(f"Vector search in AIFS failed: {e}")
        
        # Fallback to database vector search (if implemented)
        raise SearchError("Vector search not implemented for database")
    
    async def _text_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: str = "created_at",
        order: str = "desc",
        page: int = 1,
        per_page: int = 20
    ) -> AssetSearchResponse:
        """Perform text-based search."""
        # Build search query
        search_query = self.db.query(AssetModel)
        
        # Text search in name and metadata
        search_filter = or_(
            AssetModel.name.contains(query),
            AssetModel.metadata.contains({"description": query})
        )
        search_query = search_query.filter(search_filter)
        
        # Apply additional filters
        if filters:
            if "type" in filters:
                search_query = search_query.filter(AssetModel.type == filters["type"])
            if "tags" in filters:
                for tag in filters["tags"]:
                    search_query = search_query.filter(AssetModel.tags.contains([tag]))
            if "mime_type" in filters:
                search_query = search_query.filter(AssetModel.mime_type == filters["mime_type"])
        
        # Get total count
        total = search_query.count()
        
        # Apply sorting
        if hasattr(AssetModel, sort):
            sort_column = getattr(AssetModel, sort)
            if order == "desc":
                search_query = search_query.order_by(sort_column.desc())
            else:
                search_query = search_query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (page - 1) * per_page
        assets = search_query.offset(offset).limit(per_page).all()
        
        # Convert to search results
        search_results = []
        for asset in assets:
            # Calculate relevance score based on text matching
            relevance_score = self._calculate_text_relevance(query, asset.name, asset.metadata)
            
            search_results.append(AssetSearchResult(
                asset=asset,
                relevance_score=relevance_score,
                matched_fields=["name"] if query.lower() in asset.name.lower() else [],
                snippet=None
            ))
        
        return AssetSearchResponse(
            results=search_results,
            total=total,
            page=page,
            per_page=per_page,
            query_time=0.0,  # Will be set by caller
            suggestions=[]
        )
    
    def _calculate_text_relevance(self, query: str, name: str, metadata: Dict[str, Any]) -> float:
        """Calculate relevance score for text search."""
        query_lower = query.lower()
        name_lower = name.lower()
        
        # Simple relevance scoring
        if query_lower == name_lower:
            return 1.0
        elif query_lower in name_lower:
            return 0.8
        elif any(word in name_lower for word in query_lower.split()):
            return 0.6
        else:
            return 0.3
    
    async def vector_search(
        self,
        query: str,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search and return raw results."""
        try:
            if not self.embedding_service.is_available():
                raise SearchError("Embedding service not available")
            
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            if not query_embedding:
                raise SearchError("Failed to generate query embedding")
            
            # Search in AIFS if connected
            if self.aifs_manager.is_connected:
                aifs_client = self.aifs_manager.get_client()
                results = await aifs_client.vector_search(
                    query_embedding=query_embedding,
                    k=k,
                    filter_metadata=filters
                )
                return results
            
            # Fallback to empty results
            return []
            
        except Exception as e:
            raise SearchError(f"Vector search failed: {e}")
    
    async def get_suggestions(self, query: str) -> List[str]:
        """Get search suggestions based on query."""
        try:
            # Simple suggestion based on asset names
            suggestions_query = self.db.query(AssetModel.name).filter(
                AssetModel.name.contains(query)
            ).limit(10)
            
            suggestions = [row[0] for row in suggestions_query.all()]
            return suggestions
            
        except Exception as e:
            raise SearchError(f"Failed to get suggestions: {e}")
