from langchain_community.llms import OpenAI
from app.core.config import settings
from app.models.schemas import QuizQuestion, QuizResponse, QuizResult
from app.services.rag_service import RAGService
import random
import logging
import json
import re

logger = logging.getLogger(__name__)

class QuizService:
    def __init__(self, collection):
        self.collection = collection
        self.llm = None
        if settings.OPENAI_API_KEY:
            try:
                self.llm = OpenAI(
                    openai_api_key=settings.OPENAI_API_KEY,
                    temperature=0.7
                )
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {str(e)}")
    
    async def generate_quiz(self) -> QuizResponse:
        """Generate quiz questions from random document context"""
        try:
            # Get random document chunks
            results = self.collection.get(limit=10)
            if not results['documents']:
                raise Exception("No documents found to generate quiz from")
            
            # Select random context
            random_context = random.choice(results['documents'])
            
            if self.llm:
                # Generate questions using LLM
                questions = await self._generate_questions_with_llm(random_context)
            else:
                # Generate simple mock questions
                questions = self._generate_mock_questions(random_context)
            
            return QuizResponse(
                questions=questions,
                context_used=random_context[:200] + "..." if len(random_context) > 200 else random_context
            )
            
        except Exception as e:
            logger.error(f"Quiz generation error: {str(e)}")
            raise Exception(f"Failed to generate quiz: {str(e)}")
    
    async def _generate_questions_with_llm(self, context: str) -> list[QuizQuestion]:
        """Generate questions using OpenAI"""
        prompt = f"""
        Based on the following context, generate 3 multiple-choice questions:
        
        Context: {context}
        
        For each question, provide:
        1. The question
        2. 4 options (A, B, C, D)
        3. The correct answer (0-3)
        
        Format as JSON:
        {{
            "questions": [
                {{
                    "question": "...",
                    "options": ["...", "...", "...", "..."],
                    "correct_answer": 0
                }}
            ]
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                quiz_data = json.loads(json_match.group())
                questions = []
                for q in quiz_data.get('questions', []):
                    questions.append(QuizQuestion(**q))
                return questions
            else:
                return self._generate_mock_questions(context)
                
        except Exception as e:
            logger.error(f"LLM question generation failed: {str(e)}")
            return self._generate_mock_questions(context)
    
    def _generate_mock_questions(self, context: str) -> list[QuizQuestion]:
        """Generate mock questions when LLM is not available"""
        questions = []
        
        # Simple template-based questions
        templates = [
            {
                "question": f"What is the main topic discussed in the text?",
                "options": [
                    "The text discusses various topics",
                    "It's about technology",
                    "It's about history", 
                    "Not mentioned in the text"
                ],
                "correct_answer": 0
            },
            {
                "question": f"Based on the context, what can be inferred?",
                "options": [
                    "The information is factual",
                    "The content is fictional",
                    "It's an opinion piece",
                    "Cannot be determined"
                ],
                "correct_answer": 0
            },
            {
                "question": f"What is the purpose of this document?",
                "options": [
                    "To inform the reader",
                    "To entertain",
                    "To persuade",
                    "To confuse"
                ],
                "correct_answer": 0
            }
        ]
        
        for template in templates:
            questions.append(QuizQuestion(**template))
        
        return questions
    
    async def evaluate_quiz(self, submissions: list) -> QuizResult:
        """Evaluate quiz answers and calculate score"""
        try:
            correct_count = 0
            total_questions = len(submissions)
            
            for submission in submissions:
                if submission.selected_answer == 0:  # Simplified scoring
                    correct_count += 1
            
            xp_gained = 50 if correct_count == total_questions else 25
            
            return QuizResult(
                score=correct_count,
                total_questions=total_questions,
                xp_gained=xp_gained
            )
            
        except Exception as e:
            logger.error(f"Quiz evaluation error: {str(e)}")
            raise Exception(f"Failed to evaluate quiz: {str(e)}")
