"""
RAG service for document processing and chat functionality.
"""

import uuid
import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import settings
from app.core.aifs_client import AIFSClientManager
from app.core.exceptions import OpenAIError, RAGError
from app.models.conversation import Conversation as ConversationModel, Message as MessageModel, MessageSource as MessageSourceModel
from app.schemas.conversation import ChatResponse, DocumentProcessingResponse, MessageSource
from app.services.embedding_service import EmbeddingService
from app.services.asset_service import AssetService

class RAGService:
    """Service for RAG operations."""
    
    def __init__(self, db: Session, aifs_manager: AIFSClientManager):
        self.db = db
        self.aifs_manager = aifs_manager
        self.embedding_service = EmbeddingService()
        self.asset_service = AssetService(db, aifs_manager)
        
        # Initialize OpenAI client
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
    
    async def process_document(
        self,
        asset_id: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        force_reprocess: bool = False
    ) -> DocumentProcessingResponse:
        """Process a document for RAG usage."""
        start_time = time.time()
        
        try:
            # Get asset
            asset = await self.asset_service.get_asset(asset_id)
            if not asset:
                raise RAGError(f"Asset {asset_id} not found")
            
            # Check if already processed
            if asset.is_processed and not force_reprocess:
                return DocumentProcessingResponse(
                    processing_id=str(uuid.uuid4()),
                    status="already_processed",
                    chunks_created=0,
                    processing_time=time.time() - start_time
                )
            
            # TODO: Implement document processing pipeline
            # 1. Extract text from document
            # 2. Chunk text
            # 3. Generate embeddings for chunks
            # 4. Store chunks in database
            
            # For now, return mock response
            processing_time = time.time() - start_time
            
            return DocumentProcessingResponse(
                processing_id=str(uuid.uuid4()),
                status="completed",
                chunks_created=5,  # Mock value
                processing_time=processing_time
            )
            
        except Exception as e:
            raise RAGError(f"Document processing failed: {e}")
    
    async def chat(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        context_assets: Optional[List[str]] = None
    ) -> ChatResponse:
        """Handle a chat query with RAG."""
        try:
            if not self.openai_client:
                raise OpenAIError("OpenAI client not configured")
            
            # Create or get conversation
            if conversation_id:
                conversation = self.db.query(ConversationModel).filter(
                    ConversationModel.id == conversation_id
                ).first()
                if not conversation:
                    raise RAGError(f"Conversation {conversation_id} not found")
            else:
                # Create temporary conversation
                conversation = ConversationModel(
                    id=str(uuid.uuid4()),
                    title=f"Chat: {query[:50]}...",
                    created_by="system"
                )
                self.db.add(conversation)
                self.db.commit()
                self.db.refresh(conversation)
            
            # Create user message
            user_message = MessageModel(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                role="user",
                content=query
            )
            self.db.add(user_message)
            self.db.commit()
            self.db.refresh(user_message)
            
            # TODO: Implement RAG pipeline
            # 1. Generate query embedding
            # 2. Search for relevant chunks
            # 3. Retrieve context
            # 4. Generate response with OpenAI
            
            # For now, generate a simple response
            response_content = f"I received your query: '{query}'. This is a mock response from the RAG system."
            
            # Create assistant message
            assistant_message = MessageModel(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                role="assistant",
                content=response_content,
                metadata={
                    "model_used": settings.OPENAI_MODEL,
                    "tokens_used": 50,  # Mock value
                    "generation_time": 1.5  # Mock value
                }
            )
            self.db.add(assistant_message)
            self.db.commit()
            self.db.refresh(assistant_message)
            
            # Create mock sources
            sources = [
                MessageSource(
                    asset_id="mock_asset_1",
                    asset_name="Sample Document",
                    relevance_score=0.95,
                    snippet="This is a relevant snippet from the document.",
                    page_number=1,
                    chunk_index=0
                )
            ]
            
            # Store sources in database
            for source in sources:
                db_source = MessageSourceModel(
                    id=str(uuid.uuid4()),
                    message_id=assistant_message.id,
                    asset_id=source.asset_id,
                    asset_name=source.asset_name,
                    relevance_score=str(source.relevance_score),
                    snippet=source.snippet,
                    page_number=source.page_number,
                    chunk_index=source.chunk_index
                )
                self.db.add(db_source)
            
            self.db.commit()
            
            return ChatResponse(
                user_message=user_message,
                assistant_message=assistant_message,
                sources=sources,
                conversation_id=conversation.id
            )
            
        except Exception as e:
            raise RAGError(f"Chat operation failed: {e}")
    
    async def _retrieve_relevant_chunks(
        self,
        query: str,
        context_assets: Optional[List[str]] = None,
        max_chunks: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant text chunks for a query."""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            if not query_embedding:
                return []
            
            # Search in AIFS if connected
            if self.aifs_manager.is_connected:
                aifs_client = self.aifs_manager.get_client()
                results = await aifs_client.vector_search(
                    query_embedding=query_embedding,
                    k=max_chunks,
                    filter_metadata={"type": "text_chunk"}
                )
                return results
            
            # Fallback to database search
            # TODO: Implement database vector search
            return []
            
        except Exception as e:
            raise RAGError(f"Failed to retrieve relevant chunks: {e}")
    
    async def _generate_response(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[MessageModel]] = None
    ) -> str:
        """Generate response using OpenAI."""
        try:
            if not self.openai_client:
                raise OpenAIError("OpenAI client not configured")
            
            # Prepare context
            context_text = self._prepare_context(context_chunks)
            
            # Build messages
            messages = self._build_messages(query, context_text, conversation_history)
            
            # Generate response
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise OpenAIError(f"Failed to generate response: {e}")
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"Source {i} (Relevance: {chunk.get('score', 0):.2f}):\n"
                f"{chunk.get('content', '')}\n"
            )
        return "\n".join(context_parts)
    
    def _build_messages(
        self,
        query: str,
        context: str,
        history: Optional[List[MessageModel]] = None
    ) -> List[Dict[str, str]]:
        """Build messages for OpenAI API."""
        system_prompt = """You are an AI assistant that helps users find and understand information from their documents. 
        Use the provided context to answer questions accurately and cite your sources.
        If you cannot find relevant information in the context, say so clearly."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if history:
            for msg in history[-10:]:  # Limit history
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Add current query with context
        user_message = f"""Context:
{context}

Question: {query}

Please answer the question based on the provided context. If you reference specific information, cite the source number."""
        
        messages.append({"role": "user", "content": user_message})
        return messages
