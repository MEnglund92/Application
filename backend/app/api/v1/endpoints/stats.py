from fastapi import APIRouter, Depends
from app.services.rag_service import RAGService
from app.models.schemas import SystemStats
from app.api.deps import get_chroma_collection
import logging
import psutil
import os

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(collection=Depends(get_chroma_collection)):
    """Get system statistics and health metrics"""
    try:
        rag_service = RAGService(collection)
        
        # Get database stats
        doc_count = collection.count()
        vector_db_size = rag_service.get_vector_db_size()
        
        # Get recent queries (mock data for now)
        last_queries = [
            {"query": "What is machine learning?", "timestamp": "2024-01-10T10:30:00"},
            {"query": "Explain neural networks", "timestamp": "2024-01-10T10:25:00"},
            {"query": "Deep learning basics", "timestamp": "2024-01-10T10:20:00"},
        ]
        
        # System health
        system_health = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        return SystemStats(
            documents_count=doc_count,
            vector_db_size_mb=vector_db_size,
            last_queries=last_queries,
            system_health=system_health
        )
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
