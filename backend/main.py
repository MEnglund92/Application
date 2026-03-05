import os
import time
import uvicorn
import chromadb
import io
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Gemini RAG PDF")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_HOST = os.getenv("CHROMA_SERVER_HOST", "chromadb")
CHROMA_PORT = os.getenv("CHROMA_SERVER_PORT", "8000")

if not GEMINI_API_KEY:
    print("❌ CRITICAL: GEMINI_API_KEY is missing")

genai.configure(api_key=GEMINI_API_KEY)

def get_vector_store():
    retries = 10
    for i in range(retries):
        try:
            client = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
            client.heartbeat()
            print("✅ Connected to ChromaDB")
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
            return Chroma(
                client=client,
                collection_name="rag_documents",
                embedding_function=embeddings
            )
        except Exception as e:
            print(f"⏳ Waiting for DB... ({i+1}/{retries})")
            time.sleep(2)
    return None

vector_store = None

@app.on_event("startup")
async def startup_event():
    global vector_store
    vector_store = get_vector_store()

class ChatRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not vector_store:
        raise HTTPException(status_code=503, detail="Database not ready")
    
    try:
        content = await file.read()
        filename = file.filename.lower()
        text_content = ""

        if filename.endswith(".pdf"):
            try:
                pdf_reader = PdfReader(io.BytesIO(content))
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Bad PDF: {str(e)}")
        else:
            text_content = content.decode("utf-8")

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="Empty file")

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.create_documents([text_content])
        vector_store.add_documents(docs)
        
        return {"message": "Processed", "chunks": len(docs), "xp_gained": 10}
        
    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    if not vector_store:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    try:
        docs = vector_store.similarity_search(request.question, k=4)
        context = "\n\n".join([d.page_content for d in docs])
        
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Context:\n{context}\n\nQuestion: {request.question}\n\nAnswer:"
        response = model.generate_content(prompt)
        
        return {
            "response": response.text,
            "xp_gained": 2
        }
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))