from fastapi import HTTPException
from app.core.database import chroma_manager

def get_chroma_collection():
    try:
        return chroma_manager.get_or_create_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
