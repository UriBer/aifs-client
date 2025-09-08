"""
Asset service for managing assets.
"""

import hashlib
import uuid
from typing import List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, or_

from app.core.config import settings
from app.core.aifs_client import AIFSClientManager
from app.core.exceptions import AssetNotFoundError
from app.models.asset import Asset as AssetModel
from app.schemas.asset import Asset, AssetCreate, AssetUpdate
from app.services.embedding_service import EmbeddingService

class AssetService:
    """Service for asset management operations."""
    
    def __init__(self, db: Session, aifs_manager: AIFSClientManager):
        self.db = db
        self.aifs_manager = aifs_manager
        self.embedding_service = EmbeddingService()
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_file_types = settings.ALLOWED_FILE_TYPES
    
    async def list_assets(
        self,
        page: int = 1,
        per_page: int = 20,
        sort: str = "created_at",
        sort_order = desc,
        asset_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Asset], int]:
        """List assets with filtering and pagination."""
        query = self.db.query(AssetModel)
        
        # Apply filters
        if asset_type:
            query = query.filter(AssetModel.type == asset_type)
        
        if tags:
            # Filter by tags (JSON array contains)
            for tag in tags:
                query = query.filter(AssetModel.tags.contains([tag]))
        
        if search:
            # Search in name and metadata
            search_filter = or_(
                AssetModel.name.contains(search),
                AssetModel.metadata.contains({"description": search})
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if hasattr(AssetModel, sort):
            sort_column = getattr(AssetModel, sort)
            query = query.order_by(sort_order(sort_column))
        
        # Apply pagination
        offset = (page - 1) * per_page
        assets = query.offset(offset).limit(per_page).all()
        
        return [Asset.from_orm(asset) for asset in assets], total
    
    async def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Get asset by ID."""
        asset = self.db.query(AssetModel).filter(AssetModel.id == asset_id).first()
        if not asset:
            return None
        return Asset.from_orm(asset)
    
    async def create_asset(
        self,
        asset_data: AssetCreate,
        content: bytes,
        generate_embedding: bool = True
    ) -> Asset:
        """Create a new asset."""
        # Generate asset ID
        asset_id = str(uuid.uuid4())
        
        # Generate embedding if requested
        embedding = None
        if generate_embedding and asset_data.mime_type and asset_data.mime_type.startswith('text/'):
            try:
                text_content = content.decode('utf-8')
                embedding = await self.embedding_service.generate_embedding(text_content)
            except Exception as e:
                # Log error but continue without embedding
                print(f"Failed to generate embedding: {e}")
        
        # Create asset in database
        db_asset = AssetModel(
            id=asset_id,
            name=asset_data.name,
            type=asset_data.type,
            mime_type=asset_data.mime_type,
            size=asset_data.size,
            content_hash=asset_data.content_hash,
            metadata=asset_data.metadata,
            embedding=embedding,
            tags=asset_data.tags,
            is_processed=False,
            processing_status="pending"
        )
        
        self.db.add(db_asset)
        self.db.commit()
        self.db.refresh(db_asset)
        
        # Store in AIFS if connected
        if self.aifs_manager.is_connected:
            try:
                aifs_client = self.aifs_manager.get_client()
                await aifs_client.put_asset(
                    data=content,
                    kind=asset_data.type,
                    embedding=embedding,
                    metadata=asset_data.metadata,
                    parents=asset_data.parents
                )
            except Exception as e:
                # Log error but continue
                print(f"Failed to store in AIFS: {e}")
        
        return Asset.from_orm(db_asset)
    
    async def update_asset(self, asset_id: str, asset_update: AssetUpdate) -> Optional[Asset]:
        """Update an asset."""
        asset = self.db.query(AssetModel).filter(AssetModel.id == asset_id).first()
        if not asset:
            return None
        
        # Update fields
        if asset_update.name is not None:
            asset.name = asset_update.name
        if asset_update.metadata is not None:
            asset.metadata = asset_update.metadata
        if asset_update.tags is not None:
            asset.tags = asset_update.tags
        
        self.db.commit()
        self.db.refresh(asset)
        
        return Asset.from_orm(asset)
    
    async def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset."""
        asset = self.db.query(AssetModel).filter(AssetModel.id == asset_id).first()
        if not asset:
            return False
        
        # Delete from AIFS if connected
        if self.aifs_manager.is_connected:
            try:
                aifs_client = self.aifs_manager.get_client()
                # TODO: Implement delete in AIFS client
                pass
            except Exception as e:
                print(f"Failed to delete from AIFS: {e}")
        
        # Delete from database
        self.db.delete(asset)
        self.db.commit()
        
        return True
    
    async def download_asset(self, asset_id: str) -> Optional[dict]:
        """Download asset content."""
        asset = self.db.query(AssetModel).filter(AssetModel.id == asset_id).first()
        if not asset:
            return None
        
        # Try to get from AIFS first
        if self.aifs_manager.is_connected:
            try:
                aifs_client = self.aifs_manager.get_client()
                aifs_asset = await aifs_client.get_asset(asset_id)
                return {
                    "content": aifs_asset["data"],
                    "name": asset.name,
                    "mime_type": asset.mime_type
                }
            except Exception as e:
                print(f"Failed to get from AIFS: {e}")
        
        # Fallback to local storage (if implemented)
        # For now, return None as we don't have local file storage
        return None
    
    async def search_assets(
        self,
        query: str,
        filters: Optional[dict] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Asset], int]:
        """Search assets using vector similarity and text search."""
        # For now, implement basic text search
        # TODO: Implement vector search when AIFS is connected
        
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
        
        # Get total count
        total = search_query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        assets = search_query.offset(offset).limit(per_page).all()
        
        return [Asset.from_orm(asset) for asset in assets], total
