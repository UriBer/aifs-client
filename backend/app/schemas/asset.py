"""
Asset Pydantic schemas.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AssetBase(BaseModel):
    """Base asset schema."""
    name: str
    type: str = Field(..., description="Asset type: file, folder, collection")
    mime_type: Optional[str] = None
    size: int = 0
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class AssetCreate(AssetBase):
    """Schema for creating an asset."""
    content_hash: str
    embedding: Optional[List[float]] = None
    parents: Optional[List[Dict[str, str]]] = None


class AssetUpdate(BaseModel):
    """Schema for updating an asset."""
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class Asset(AssetBase):
    """Complete asset schema."""
    id: str
    content_hash: str
    embedding: Optional[List[float]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    is_processed: bool = False
    processing_status: str = "pending"
    
    class Config:
        from_attributes = True


class AssetRelationshipBase(BaseModel):
    """Base asset relationship schema."""
    parent_id: str
    child_id: str
    relationship_type: str
    transform_name: Optional[str] = None
    transform_digest: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AssetRelationship(AssetRelationshipBase):
    """Complete asset relationship schema."""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TextChunkBase(BaseModel):
    """Base text chunk schema."""
    asset_id: str
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Optional[Dict[str, Any]] = None


class TextChunk(TextChunkBase):
    """Complete text chunk schema."""
    id: str
    embedding: Optional[List[float]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssetUpload(BaseModel):
    """Schema for asset upload."""
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    parents: Optional[List[str]] = None
    generate_embedding: bool = True


class AssetListResponse(BaseModel):
    """Schema for asset list response."""
    assets: List[Asset]
    total: int
    page: int
    per_page: int
    pages: int


class AssetSearchQuery(BaseModel):
    """Schema for asset search query."""
    query: str
    filters: Optional[Dict[str, Any]] = None
    sort: Optional[str] = "created_at"
    order: Optional[str] = "desc"
    page: int = 1
    per_page: int = 20
    include_embeddings: bool = False


class AssetSearchResult(BaseModel):
    """Schema for asset search result."""
    asset: Asset
    relevance_score: float
    matched_fields: List[str]
    snippet: Optional[str] = None


class AssetSearchResponse(BaseModel):
    """Schema for asset search response."""
    results: List[AssetSearchResult]
    total: int
    page: int
    per_page: int
    query_time: float
    suggestions: List[str] = []
