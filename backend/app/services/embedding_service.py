"""
Embedding service for generating text embeddings using OpenAI.
"""

import logging
from typing import List, Optional
import openai
from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import OpenAIError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured. Embedding generation will be disabled.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_EMBEDDING_MODEL
            self.dimension = 1536  # ada-002 dimension
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text."""
        if not self.client:
            logger.warning("OpenAI client not available. Skipping embedding generation.")
            return None
        
        try:
            # Truncate text if too long (OpenAI has limits)
            max_chars = 8000  # Conservative limit for ada-002
            if len(text) > max_chars:
                text = text[:max_chars]
            
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise OpenAIError(f"Failed to generate embedding: {e}")
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts."""
        if not self.client:
            logger.warning("OpenAI client not available. Skipping embedding generation.")
            return [None] * len(texts)
        
        try:
            # Truncate texts if too long
            max_chars = 8000
            truncated_texts = [text[:max_chars] if len(text) > max_chars else text for text in texts]
            
            response = self.client.embeddings.create(
                input=truncated_texts,
                model=self.model
            )
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise OpenAIError(f"Failed to generate batch embeddings: {e}")
    
    async def generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """Generate embedding for a search query."""
        return await self.generate_embedding(query)
    
    def is_available(self) -> bool:
        """Check if embedding service is available."""
        return self.client is not None
