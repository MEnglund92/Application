from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
from typing import List
from dotenv import load_dotenv
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import HumanMessage
import PyPDF2
import io

# Load environment variables
load_dotenv()

app = FastAPI(title="RAG Gamified Platform")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY not set")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="/chroma/chroma")
collection = chroma_client.get_or_create_collection(name="documents")

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

# XP System
user_xp = {"current_xp": 0, "level": 1}
XP_PER_LEVEL = 100

class ChatRequest(BaseModel):
    question: str

class UploadResponse(BaseModel):
    message: str
    xp_gained: int

class ChatResponse(BaseModel):
    response: str
    xp_gained: int

class QuizResponse(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    xp_gained: int

def calculate_xp(xp_gained: int):
    user_xp["current_xp"] += xp_gained
    if user_xp["current_xp"] >= XP_PER_LEVEL:
        user_xp["level"] += 1
        user_xp["current_xp"] = user_xp["current_xp"] % XP_PER_LEVEL
    return user_xp

@app.get("/")
async def root():
    return {"message": "RAG Gamified Platform API"}

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    content = await file.read()
    
    # Extract text from PDF or read text file
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    else:
        text = content.decode('utf-8')
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    
    # Store in ChromaDB
    for i, chunk in enumerate(chunks):
        doc_id = str(uuid.uuid4())
        embedding = embeddings.embed_query(chunk)
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[doc_id]
        )
    
    # Award XP
    xp_state = calculate_xp(10)
    
    return UploadResponse(message=f"Successfully uploaded and processed {len(chunks)} chunks", xp_gained=10)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    # Search ChromaDB for relevant context
    query_embedding = embeddings.embed_query(request.question)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    
    context = " ".join(results["documents"][0]) if results["documents"] else ""
    
    # Generate response with Gemini
    prompt = f"Context: {context}\n\nQuestion: {request.question}\n\nAnswer based on the context provided:"
    response = llm([HumanMessage(content=prompt)])
    
    # Award XP
    xp_state = calculate_xp(2)
    
    return ChatResponse(response=response.content, xp_gained=2)

@app.get("/quiz", response_model=QuizResponse)
async def generate_quiz():
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    # Get random chunks
    results = collection.get(limit=3)
    context = " ".join(results["documents"]) if results["documents"] else "Sample text for quiz generation"
    
    # Generate quiz question
    prompt = f"Generate a multiple choice question based on this text: {context}\n\nReturn in format:\nQuestion: [question]\nA. [option1]\nB. [option2]\nC. [option3]\nD. [option4]\nCorrect: [A/B/C/D]"
    response = llm([HumanMessage(content=prompt)])
    
    # Parse response (simplified parsing)
    lines = response.content.split('\n')
    question = lines[0].replace("Question: ", "")
    options = [line[3:] for line in lines[1:5]]
    correct_line = lines[5] if len(lines) > 5 else "A"
    correct_answer = ord(correct_line[-1]) - ord('A')
    
    # Award XP
    xp_state = calculate_xp(50)
    
    return QuizResponse(
        question=question,
        options=options,
        correct_answer=correct_answer,
        xp_gained=50
    )

@app.get("/stats")
async def get_stats():
    return user_xp
