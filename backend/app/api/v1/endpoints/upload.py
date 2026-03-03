from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.rag_service import RAGService
from app.models.schemas import DocumentUploadResponse
from app.api.deps import get_chroma_collection
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection=Depends(get_chroma_collection)
):
    """Upload and process a document"""
    try:
        rag_service = RAGService(collection)
        
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF and TXT files are supported"
            )
        
        chunks_processed = await rag_service.process_document(file)
        
        logger.info(f"Processed {chunks_processed} chunks from {file.filename}")
        
        return DocumentUploadResponse(
            message="Document uploaded and processed successfully",
            filename=file.filename,
            chunks_processed=chunks_processed,
            xp_gained=10
        )
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
