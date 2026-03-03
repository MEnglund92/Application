from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.rag_service import RAGService
from app.models.schemas import SearchResponse
from app.api.deps import get_chroma_collection
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    collection=Depends(get_chroma_collection)
):
    """Search documents using semantic similarity"""
    try:
        rag_service = RAGService(collection)
        results = await rag_service.search(request.query, request.max_results)
        
        logger.info(f"Search query: '{request.query}' - Found {len(results)} results")
        
        return SearchResponse(
            query=request.query,
            results=results,
            xp_gained=2
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
