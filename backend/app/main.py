from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import upload, search, quiz, stats
from app.core.config import settings

app = FastAPI(
    title="RAG Gamified Learning API",
    description="API for document processing and gamified learning",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(quiz.router, prefix="/api/v1", tags=["quiz"])
app.include_router(stats.router, prefix="/api/v1", tags=["stats"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "RAG Gamified Learning API"}
