"""
Asset database model.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Asset(Base):
    """Asset model for storing asset metadata."""
    
    __tablename__ = "assets"
    
    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # file, folder, collection
    mime_type = Column(String(100), nullable=True)
    size = Column(Integer, nullable=False, default=0)
    content_hash = Column(String(64), nullable=False, index=True)
    asset_metadata = Column(JSON, nullable=True)
    embedding = Column(JSON, nullable=True)  # Store as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)  # Store as JSON array
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")
    
    def __repr__(self):
        return f"<Asset(id='{self.id}', name='{self.name}', type='{self.type}')>"


class AssetRelationship(Base):
    """Asset relationship model for lineage tracking."""
    
    __tablename__ = "asset_relationships"
    
    id = Column(String(255), primary_key=True, index=True)
    parent_id = Column(String(255), nullable=False, index=True)
    child_id = Column(String(255), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False)  # derived, transformed, contains
    transform_name = Column(String(255), nullable=True)
    transform_digest = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    asset_metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<AssetRelationship(parent='{self.parent_id}', child='{self.child_id}', type='{self.relationship_type}')>"


class TextChunk(Base):
    """Text chunk model for RAG processing."""
    
    __tablename__ = "text_chunks"
    
    id = Column(String(255), primary_key=True, index=True)
    asset_id = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    embedding = Column(JSON, nullable=True)  # Store as JSON array
    asset_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TextChunk(id='{self.id}', asset_id='{self.asset_id}', index={self.chunk_index})>"
