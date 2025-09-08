"""
Conversation service for managing RAG conversations.
"""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_

from app.core.aifs_client import AIFSClientManager
from app.models.conversation import Conversation as ConversationModel
from app.schemas.conversation import Conversation, ConversationCreate, ConversationUpdate

class ConversationService:
    """Service for conversation management operations."""
    
    def __init__(self, db: Session, aifs_manager: AIFSClientManager):
        self.db = db
        self.aifs_manager = aifs_manager
    
    async def list_conversations(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None
    ) -> Tuple[List[Conversation], int]:
        """List conversations with pagination and search."""
        query = self.db.query(ConversationModel)
        
        # Apply search filter
        if search:
            search_filter = or_(
                ConversationModel.title.contains(search)
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply sorting (newest first)
        query = query.order_by(desc(ConversationModel.updated_at))
        
        # Apply pagination
        offset = (page - 1) * per_page
        conversations = query.offset(offset).limit(per_page).all()
        
        return [Conversation.from_orm(conv) for conv in conversations], total
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID."""
        conversation = self.db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        
        if not conversation:
            return None
        
        return Conversation.from_orm(conversation)
    
    async def create_conversation(self, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        conversation_id = str(uuid.uuid4())
        
        db_conversation = ConversationModel(
            id=conversation_id,
            title=conversation_data.title,
            settings=conversation_data.settings.dict() if conversation_data.settings else None,
            created_by="system"  # TODO: Get from authentication
        )
        
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        
        return Conversation.from_orm(db_conversation)
    
    async def update_conversation(
        self,
        conversation_id: str,
        conversation_update: ConversationUpdate
    ) -> Optional[Conversation]:
        """Update a conversation."""
        conversation = self.db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        
        if not conversation:
            return None
        
        # Update fields
        if conversation_update.title is not None:
            conversation.title = conversation_update.title
        if conversation_update.settings is not None:
            conversation.settings = conversation_update.settings.dict()
        
        self.db.commit()
        self.db.refresh(conversation)
        
        return Conversation.from_orm(conversation)
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        conversation = self.db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        
        if not conversation:
            return False
        
        self.db.delete(conversation)
        self.db.commit()
        
        return True
