import os
import time
import subprocess
import tempfile
import shutil
import uvicorn
import chromadb
import io
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from pypdf import PdfReader
from dotenv import load_dotenv
import requests

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
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL", "")
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

def download_github_folder(repo_url, branch="main"):
    """Clone/fetch files from GitHub repo"""
    temp_dir = tempfile.mkdtemp()
    try:
        if repo_url.startswith("https://github.com"):
            api_url = repo_url.replace("github.com", "raw.githubusercontent.com").replace("/tree/", "/")
            api_url = api_url.rstrip('/') + "/" + branch + "/"
            
            response = requests.get(api_url)
            if response.status_code == 404:
                api_url = api_url.replace("/" + branch + "/", "/main/")
                response = requests.get(api_url)
            
            if response.status_code == 200:
                files = []
                for line in response.text.split('\n'):
                    if '"name"' in line and '"pdf"' in line.lower():
                        start = line.find('"name":"') + 8
                        end = line.find('"', start)
                        if start > 7 and end > start:
                            filename = line[start:end]
                            if filename.endswith('.pdf'):
                                file_url = api_url + filename
                                print(f"📥 Downloading: {filename}")
                                file_resp = requests.get(file_url)
                                if file_resp.status_code == 200:
                                    files.append((filename, file_resp.content))
                return files
    except Exception as e:
        print(f"GitHub download error: {e}")
    return []

def process_pdf(content, filename):
    """Extract text from PDF"""
    try:
        pdf_reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return ""

vector_store = None

@app.on_event("startup")
async def startup_event():
    global vector_store
    vector_store = get_vector_store()
    
    if GITHUB_REPO_URL and vector_store:
        print(f"📂 Loading files from GitHub: {GITHUB_REPO_URL}")
        await load_github_files()

async def load_github_files():
    global vector_store
    try:
        files = download_github_folder(GITHUB_REPO_URL)
        
        if not files:
            print("⚠️ No PDF files found in repo")
            return
            
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        total_chunks = 0
        
        for filename, content in files:
            text = process_pdf(content, filename)
            if text.strip():
                docs = splitter.create_documents([text])
                vector_store.add_documents(docs)
                total_chunks += len(docs)
                print(f"✅ Processed {filename}: {len(docs)} chunks")
        
        print(f"🎉 Total chunks added: {total_chunks}")
        
    except Exception as e:
        print(f"Load error: {e}")

@app.get("/status")
async def get_status():
    return {
        "github_repo": GITHUB_REPO_URL if GITHUB_REPO_URL else "Not configured",
        "vector_store_ready": vector_store is not None
    }

@app.get("/reload")
async def reload_from_github():
    global vector_store
    if not vector_store:
        raise HTTPException(status_code=503, detail="Database not ready")
    if not GITHUB_REPO_URL:
        raise HTTPException(status_code=400, detail="GITHUB_REPO_URL not configured")
    
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
        client.delete_collection("rag_documents")
        vector_store = get_vector_store()
        await load_github_files()
        return {"message": "Reloaded from GitHub"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(request: ChatRequest):
    if not vector_store:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    try:
        docs = vector_store.similarity_search(request.question, k=4)
        context = "\n\n".join([d.page_content for d in docs])
        
        if not context:
            return {"response": "No documents loaded. Please configure GITHUB_REPO_URL in .env file.", "xp_gained": 0}
        
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
