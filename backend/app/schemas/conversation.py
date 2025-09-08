"""
Conversation and RAG Pydantic schemas.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class RAGSettings(BaseModel):
    """RAG settings schema."""
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 4000
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_context_chunks: int = 10


class ConversationBase(BaseModel):
    """Base conversation schema."""
    title: str
    settings: Optional[RAGSettings] = None


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""
    context_assets: Optional[List[str]] = None


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: Optional[str] = None
    settings: Optional[RAGSettings] = None


class Conversation(ConversationBase):
    """Complete conversation schema."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class MessageSource(BaseModel):
    """Message source schema."""
    asset_id: str
    asset_name: str
    relevance_score: float
    snippet: Optional[str] = None
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None


class MessageBase(BaseModel):
    """Base message schema."""
    role: str = Field(..., description="Message role: user, assistant, system")
    content: str
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    context_assets: Optional[List[str]] = None


class Message(MessageBase):
    """Complete message schema."""
    id: str
    conversation_id: str
    created_at: datetime
    sources: List[MessageSource] = []
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Schema for chat response."""
    user_message: Message
    assistant_message: Message
    sources: List[MessageSource]
    conversation_id: str


class ConversationListResponse(BaseModel):
    """Schema for conversation list response."""
    conversations: List[Conversation]
    total: int
    page: int
    per_page: int
    pages: int


class DocumentProcessingRequest(BaseModel):
    """Schema for document processing request."""
    asset_id: str
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    force_reprocess: bool = False


class DocumentProcessingResponse(BaseModel):
    """Schema for document processing response."""
    processing_id: str
    status: str
    chunks_created: int
    processing_time: float
