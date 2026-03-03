from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    message: str
    filename: str
    chunks_processed: int
    xp_gained: int

class SearchResult(BaseModel):
    content: str
    source: str
    page: Optional[int] = None
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    xp_gained: int

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]
    context_used: str

class QuizSubmission(BaseModel):
    question_id: int
    selected_answer: int

class QuizResult(BaseModel):
    score: int
    total_questions: int
    xp_gained: int

class SystemStats(BaseModel):
    documents_count: int
    vector_db_size_mb: float
    last_queries: List[Dict[str, Any]]
    system_health: Dict[str, float]
