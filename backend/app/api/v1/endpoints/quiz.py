from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.quiz_service import QuizService
from app.models.schemas import QuizResponse, QuizResult, QuizSubmission
from app.api.deps import get_chroma_collection
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/quiz", response_model=QuizResponse)
async def generate_quiz(collection=Depends(get_chroma_collection)):
    """Generate a quiz from random document context"""
    try:
        quiz_service = QuizService(collection)
        quiz_data = await quiz_service.generate_quiz()
        
        logger.info(f"Generated quiz with {len(quiz_data.questions)} questions")
        
        return quiz_data
        
    except Exception as e:
        logger.error(f"Quiz generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz/submit", response_model=QuizResult)
async def submit_quiz(
    submission: list[QuizSubmission],
    collection=Depends(get_chroma_collection)
):
    """Submit quiz answers and calculate score"""
    try:
        quiz_service = QuizService(collection)
        result = await quiz_service.evaluate_quiz(submission)
        
        logger.info(f"Quiz submitted: Score {result.score}/{result.total_questions}")
        
        return result
        
    except Exception as e:
        logger.error(f"Quiz submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
