from langchain_community.embeddings import OpenAIEmbeddings
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.embeddings = None
        if settings.OPENAI_API_KEY:
            try:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.OPENAI_API_KEY
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI embeddings: {str(e)}")
    
    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for text"""
        if not self.embeddings:
            raise Exception("Embeddings not available. Please set OPENAI_API_KEY.")
        
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if embedding service is available"""
        return self.embeddings is not None
