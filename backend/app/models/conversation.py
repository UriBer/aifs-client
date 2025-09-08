"""
Conversation and RAG models.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Conversation(Base):
    """Conversation model for RAG chat sessions."""
    
    __tablename__ = "conversations"
    
    id = Column(String(255), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    settings = Column(JSON, nullable=True)  # RAG settings
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    context_assets = relationship("ConversationAsset", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id='{self.id}', title='{self.title}')>"


class Message(Base):
    """Message model for RAG chat messages."""
    
    __tablename__ = "messages"
    
    id = Column(String(255), primary_key=True, index=True)
    conversation_id = Column(String(255), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    conversation_metadata = Column(JSON, nullable=True)  # Model info, tokens used, etc.
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sources = relationship("MessageSource", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Message(id='{self.id}', role='{self.role}', conversation_id='{self.conversation_id}')>"


class MessageSource(Base):
    """Message source model for RAG source attribution."""
    
    __tablename__ = "message_sources"
    
    id = Column(String(255), primary_key=True, index=True)
    message_id = Column(String(255), ForeignKey("messages.id"), nullable=False)
    asset_id = Column(String(255), nullable=False)
    asset_name = Column(String(255), nullable=False)
    relevance_score = Column(String(20), nullable=False)  # Store as string to preserve precision
    snippet = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    chunk_index = Column(Integer, nullable=True)
    
    # Relationships
    message = relationship("Message", back_populates="sources")
    
    def __repr__(self):
        return f"<MessageSource(id='{self.id}', asset_id='{self.asset_id}', score='{self.relevance_score}')>"


class ConversationAsset(Base):
    """Conversation asset model for tracking context assets."""
    
    __tablename__ = "conversation_assets"
    
    id = Column(String(255), primary_key=True, index=True)
    conversation_id = Column(String(255), ForeignKey("conversations.id"), nullable=False)
    asset_id = Column(String(255), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="context_assets")
    
    def __repr__(self):
        return f"<ConversationAsset(conversation_id='{self.conversation_id}', asset_id='{self.asset_id}')>"
