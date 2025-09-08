"""
Conversation and RAG endpoints.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.aifs_client import AIFSClientManager
from app.schemas.conversation import (
    Conversation, ConversationCreate, ConversationUpdate, ConversationListResponse,
    Message, MessageCreate, ChatResponse, DocumentProcessingRequest, DocumentProcessingResponse
)
from app.services.conversation_service import ConversationService
from app.services.rag_service import RAGService

router = APIRouter()


def get_conversation_service(
    db: Session = Depends(get_db),
    aifs_manager: AIFSClientManager = Depends(lambda: AIFSClientManager())
) -> ConversationService:
    """Get conversation service instance."""
    return ConversationService(db, aifs_manager)


def get_rag_service(
    db: Session = Depends(get_db),
    aifs_manager: AIFSClientManager = Depends(lambda: AIFSClientManager())
) -> RAGService:
    """Get RAG service instance."""
    return RAGService(db, aifs_manager)


@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """List conversations."""
    try:
        conversations, total = await conversation_service.list_conversations(
            page=page,
            per_page=per_page,
            search=search
        )
        
        pages = (total + per_page - 1) // per_page
        
        return ConversationListResponse(
            conversations=conversations,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Conversation)
async def create_conversation(
    conversation_data: ConversationCreate,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Create a new conversation."""
    try:
        conversation = await conversation_service.create_conversation(conversation_data)
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get conversation by ID."""
    try:
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: str,
    conversation_update: ConversationUpdate,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Update a conversation."""
    try:
        conversation = await conversation_service.update_conversation(conversation_id, conversation_update)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Delete a conversation."""
    try:
        success = await conversation_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Send a message in a conversation."""
    try:
        response = await rag_service.chat(
            query=message_data.content,
            conversation_id=conversation_id,
            context_assets=message_data.context_assets
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message_data: MessageCreate,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Send a message without a conversation (creates temporary conversation)."""
    try:
        response = await rag_service.chat(
            query=message_data.content,
            context_assets=message_data.context_assets
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process", response_model=DocumentProcessingResponse)
async def process_document(
    request: DocumentProcessingRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Process a document for RAG usage."""
    try:
        result = await rag_service.process_document(
            asset_id=request.asset_id,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            force_reprocess=request.force_reprocess
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
