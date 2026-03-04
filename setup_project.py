import os
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
# Tries to use your requested path, falls back to current folder if permissions fail
REQUESTED_ROOT = Path("/Users/mattias/Documents/GitHub/Application")
CURRENT_ROOT = Path.cwd() / "gemini_rag_app"

def get_target_dir():
    try:
        if not REQUESTED_ROOT.parent.exists():
            return CURRENT_ROOT
        REQUESTED_ROOT.mkdir(parents=True, exist_ok=True)
        return REQUESTED_ROOT
    except Exception:
        return CURRENT_ROOT

PROJECT_ROOT = get_target_dir()

# --- Content Generators ---

def get_gitignore():
    return """
.env
.DS_Store
__pycache__/
node_modules/
dist/
.venv/
venv/
*.pyc
"""

def get_docker_compose():
    # 1. Pinned Chromadb version for stability
    # 2. Exposed ports for local debugging
    return """version: '3.8'

services:
  backend:
    build: ./backend
    container_name: gemini_backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - CHROMA_SERVER_HOST=chromadb
      - CHROMA_SERVER_PORT=8000
    volumes:
      - ./backend:/app
    networks:
      - rag_network
    depends_on:
      - chromadb

  frontend:
    build: ./frontend
    container_name: gemini_frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - rag_network
    environment:
      - CHOKIDAR_USEPOLLING=true

  chromadb:
    image: chromadb/chroma:0.4.22
    container_name: gemini_db
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    networks:
      - rag_network
    environment:
      - IS_PERSISTENT=TRUE

networks:
  rag_network:
    driver: bridge

volumes:
  chroma_data:
"""

def get_backend_dockerfile():
    return """FROM python:3.10-slim
WORKDIR /app
# Install system tools needed for some python packages
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# host 0.0.0.0 is REQUIRED for Docker
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""

def get_backend_requirements():
    # Added pypdf so you can upload PDFs!
    return """fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
pypdf==3.17.4
langchain==0.1.0
langchain-community==0.0.10
langchain-google-genai==0.0.6
chromadb==0.4.22
python-dotenv==1.0.0
pydantic==2.5.3
google-generativeai==0.3.2
"""

def get_backend_main():
    return """import os
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
from langchain.docstore.document import Document
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Gemini RAG with PDF Support")

# CORS - Allow everything for development ease
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Config ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_HOST = os.getenv("CHROMA_SERVER_HOST", "chromadb")
CHROMA_PORT = os.getenv("CHROMA_SERVER_PORT", "8000")

if not GEMINI_API_KEY:
    print("❌ CRITICAL: GEMINI_API_KEY is missing from .env")

genai.configure(api_key=GEMINI_API_KEY)

# --- Database Connection (Robust Retry Logic) ---
def get_vector_store():
    retries = 12
    for i in range(retries):
        try:
            # We use HttpClient to talk to the Docker container 'chromadb'
            client = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
            client.heartbeat() 
            print("✅ Backend connected to ChromaDB successfully.")
            
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
            return Chroma(
                client=client,
                collection_name="rag_documents",
                embedding_function=embeddings
            )
        except Exception as e:
            print(f"⏳ Waiting for Database... ({i+1}/{retries})")
            time.sleep(3)
    print("❌ Could not connect to ChromaDB. The app may crash.")
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

        # --- PDF PARSING LOGIC ---
        if filename.endswith(".pdf"):
            try:
                pdf_reader = PdfReader(io.BytesIO(content))
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\\n"
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid PDF file: {str(e)}")
        else:
            # Assume text/markdown
            text_content = content.decode("utf-8")

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="File is empty or could not be read")

        # Split text for better AI understanding
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.create_documents([text_content])
        
        # Save to Vector DB
        vector_store.add_documents(docs)
        
        return {"message": f"Processed {filename}", "chunks": len(docs), "xp_gained": 10}
        
    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    if not vector_store:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    try:
        # 1. Search the DB for relevant document chunks
        docs = vector_store.similarity_search(request.question, k=4)
        context = "\\n\\n".join([d.page_content for d in docs])
        
        # 2. Ask Gemini
        model = genai.GenerativeModel('gemini-pro')
        
        # System Prompt
        prompt = f"You are a helpful assistant. Answer the question based ONLY on the context below.\\n\\nContext:\\n{context}\\n\\nQuestion: {request.question}\\n\\nAnswer:"
        
        response = model.generate_content(prompt)
        
        return {
            "response": response.text,
            "context_used": context[:150] + "...",
            "xp_gained": 2
        }
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
"""

def get_frontend_dockerfile():
    return """FROM node:18-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
# 0.0.0.0 is required for Docker networking
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
"""

def get_vite_config():
    return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Listen on all IPs
    watch: { usePolling: true }, // Fix for Docker file changes not detecting
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})"""

def get_frontend_files():
    pkg = """{
  "name": "gemini-rag-ui",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": { "dev": "vite", "build": "vite build", "preview": "vite preview" },
  "dependencies": { "axios": "^1.6.0", "lucide-react": "^0.300.0", "react": "^18.2.0", "react-dom": "^18.2.0", "react-markdown": "^9.0.0", "zustand": "^4.5.0" },
  "devDependencies": { "@types/react": "^18.2.43", "@types/react-dom": "^18.2.17", "@vitejs/plugin-react": "^4.2.1", "autoprefixer": "^10.4.16", "postcss": "^8.4.32", "tailwindcss": "^3.4.0", "vite": "^5.0.8" }
}"""

    # Updated UI to handle PDF Uploads visualy
    app_jsx = """import { useState } from 'react'
import { create } from 'zustand'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { Terminal, Upload, Play, FileText } from 'lucide-react'

const useStore = create((set) => ({
  xp: 0,
  level: 1,
  addXp: (amount) => set((state) => ({ xp: state.xp + amount, level: Math.floor((state.xp + amount) / 100) + 1 }))
}))

export default function App() {
  const { xp, level, addXp } = useStore()
  const [query, setQuery] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    setUploadStatus('UPLOADING...')
    const formData = new FormData()
    formData.append('file', file)
    
    try {
        setLoading(true)
        const res = await axios.post('/api/upload', formData)
        addXp(res.data.xp_gained)
        setUploadStatus('SUCCESS: ' + file.name)
        alert('DOCUMENT EMBEDDED. AI CAN NOW READ IT.')
    } catch (err) { 
        console.error(err)
        setUploadStatus('FAILED. SEE CONSOLE.')
        alert('UPLOAD FAILED: ' + (err.response?.data?.detail || err.message))
    } finally { 
        setLoading(false) 
    }
  }

  const handleChat = async () => {
    if (!query) return
    const newHist = [...history, { role: 'user', content: query }]
    setHistory(newHist)
    setQuery('')
    try {
        setLoading(true)
        const res = await axios.post('/api/chat', { question: query })
        setHistory([...newHist, { role: 'bot', content: res.data.response }])
        addXp(res.data.xp_gained)
    } catch (err) { 
        setHistory([...newHist, { role: 'err', content: "ERROR: Connection refused. Is Docker running?" }]) 
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-black text-cyan-400 p-6 font-mono selection:bg-cyan-900">
      <div className="border-b border-cyan-800 pb-4 mb-6 flex justify-between items-center">
        <h1 className="text-xl font-bold tracking-widest flex items-center gap-2"><Terminal size={20}/> GEMINI_RAG_OS</h1>
        <div className="text-right">
            <div className="text-xs text-cyan-700">LEVEL {level}</div>
            <div className="w-32 h-2 bg-cyan-900 mt-1"><div className="h-full bg-cyan-400" style={{width: `${xp % 100}%`}}></div></div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-4 border border-cyan-800 rounded bg-cyan-900/10 h-fit">
            <h2 className="mb-4 text-sm font-bold flex gap-2 items-center"><Upload size={14}/> INGEST DOCUMENT</h2>
            <div className="border-2 border-dashed border-cyan-900 p-4 text-center hover:bg-cyan-900/20 transition-colors cursor-pointer relative">
                <input type="file" onChange={handleUpload} accept=".pdf,.txt,.md" className="absolute inset-0 opacity-0 cursor-pointer"/>
                <FileText className="mx-auto mb-2 opacity-50"/>
                <div className="text-[10px] text-cyan-600">DROP PDF / TXT HERE</div>
            </div>
            {uploadStatus && <div className="mt-2 text-[10px] text-center">{uploadStatus}</div>}
        </div>

        <div className="md:col-span-3 border border-cyan-800 rounded bg-cyan-900/5 h-[600px] flex flex-col relative overflow-hidden">
            <div className="flex-1 overflow-auto space-y-4 p-4">
                {history.length === 0 && <div className="text-cyan-800 text-center mt-20 opacity-50">SYSTEM ONLINE. UPLOAD PDF TO BEGIN.</div>}
                {history.map((m, i) => (
                    <div key={i} className={`p-3 text-sm ${m.role === 'user' ? 'text-right text-white' : 'text-cyan-400'}`}>
                        <div className="text-[10px] opacity-50 mb-1">{m.role.toUpperCase()}</div>
                        <ReactMarkdown>{m.content}</ReactMarkdown>
                    </div>
                ))}
            </div>
            <div className="p-4 border-t border-cyan-800 bg-black flex gap-2">
                <input value={query} onChange={e => setQuery(e.target.value)} 
                       onKeyDown={e => e.key === 'Enter' && handleChat()}
                       className="flex-1 bg-cyan-900/20 border border-cyan-800 p-2 text-cyan-100 outline-none focus:border-cyan-400 transition-colors" placeholder="Ask about the document..."/>
                <button onClick={handleChat} className="bg-cyan-700 hover:bg-cyan-600 text-black font-bold px-6 flex items-center justify-center"><Play size={16}/></button>
            </div>
        </div>
      </div>
    </div>
  )
}"""

    return {
        "frontend/package.json": pkg,
        "frontend/vite.config.js": get_vite_config(),
        "frontend/tailwind.config.js": "export default { content: ['./src/**/*.{js,jsx}'], theme: { extend: {} }, plugins: [] }",
        "frontend/postcss.config.js": "export default { plugins: { tailwindcss: {}, autoprefixer: {} } }",
        "frontend/index.html": "<!doctype html><html><head><title>Gemini RAG</title></head><body><div id='root'></div><script type='module' src='/src/main.jsx'></script></body></html>",
        "frontend/src/main.jsx": "import React from 'react'; import ReactDOM from 'react-dom/client'; import App from './App'; import './index.css'; ReactDOM.createRoot(document.getElementById('root')).render(<App />);",
        "frontend/src/App.jsx": app_jsx,
        "frontend/src/index.css": "@tailwind base; @tailwind components; @tailwind utilities;"
    }

# --- Execution ---

def main():
    print(f"🚀 INITIALIZING SETUP TARGET: {PROJECT_ROOT}")
    
    # 1. Create Directories
    for d in [".vscode", "backend", "frontend/src", "frontend/public", "docker"]:
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)

    # 2. Prepare Files
    files = {
        ".gitignore": get_gitignore(),
        ".env": "GEMINI_API_KEY=replace_with_your_key_here",
        "docker-compose.yml": get_docker_compose(),
        "backend/Dockerfile": get_backend_dockerfile(),
        "backend/requirements.txt": get_backend_requirements(),
        "backend/main.py": get_backend_main(),
        "frontend/Dockerfile": get_frontend_dockerfile(),
    }
    files.update(get_frontend_files())

    # 3. Write Files
    for path, content in files.items():
        full_path = PROJECT_ROOT / path
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            print(f"   -> Created {path}")
        except Exception as e:
            print(f"   ❌ Error creating {path}: {e}")

    # 4. Final instructions
    print("\n" + "="*60)
    print("✅ PROJECT GENERATION COMPLETE (PDF SUPPORT ENABLED)")
    print("="*60)
    print(f"📂 Project location: {PROJECT_ROOT}")
    print("⚠️  STEP 1: Open .env and paste your GEMINI_API_KEY")
    print("🚀 STEP 2: Run the following commands:")
    print(f"   cd {PROJECT_ROOT}")
    print("   docker-compose up --build")
    print("\n🌐 App URL: http://localhost:5173")
    print("="*60)

if __name__ == "__main__":
    main()import os
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
# Tries to use your requested path, falls back to current folder if permissions fail
REQUESTED_ROOT = Path("/Users/mattias/Documents/GitHub/Application")
CURRENT_ROOT = Path.cwd() / "gemini_rag_app"

def get_target_dir():
    try:
        if not REQUESTED_ROOT.parent.exists():
            return CURRENT_ROOT
        REQUESTED_ROOT.mkdir(parents=True, exist_ok=True)
        return REQUESTED_ROOT
    except Exception:
        return CURRENT_ROOT

PROJECT_ROOT = get_target_dir()

# --- Content Generators ---

def get_gitignore():
    return """
.env
.DS_Store
__pycache__/
node_modules/
dist/
.venv/
venv/
*.pyc
"""

def get_docker_compose():
    # 1. Pinned Chromadb version for stability
    # 2. Exposed ports for local debugging
    return """version: '3.8'

services:
  backend:
    build: ./backend
    container_name: gemini_backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - CHROMA_SERVER_HOST=chromadb
      - CHROMA_SERVER_PORT=8000
    volumes:
      - ./backend:/app
    networks:
      - rag_network
    depends_on:
      - chromadb

  frontend:
    build: ./frontend
    container_name: gemini_frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - rag_network
    environment:
      - CHOKIDAR_USEPOLLING=true

  chromadb:
    image: chromadb/chroma:0.4.22
    container_name: gemini_db
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    networks:
      - rag_network
    environment:
      - IS_PERSISTENT=TRUE

networks:
  rag_network:
    driver: bridge

volumes:
  chroma_data:
"""

def get_backend_dockerfile():
    return """FROM python:3.10-slim
WORKDIR /app
# Install system tools needed for some python packages
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# host 0.0.0.0 is REQUIRED for Docker
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""

def get_backend_requirements():
    # Added pypdf so you can upload PDFs!
    return """fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
pypdf==3.17.4
langchain==0.1.0
langchain-community==0.0.10
langchain-google-genai==0.0.6
chromadb==0.4.22
python-dotenv==1.0.0
pydantic==2.5.3
google-generativeai==0.3.2
"""

def get_backend_main():
    return """import os
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
from langchain.docstore.document import Document
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Gemini RAG with PDF Support")

# CORS - Allow everything for development ease
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Config ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_HOST = os.getenv("CHROMA_SERVER_HOST", "chromadb")
CHROMA_PORT = os.getenv("CHROMA_SERVER_PORT", "8000")

if not GEMINI_API_KEY:
    print("❌ CRITICAL: GEMINI_API_KEY is missing from .env")

genai.configure(api_key=GEMINI_API_KEY)

# --- Database Connection (Robust Retry Logic) ---
def get_vector_store():
    retries = 12
    for i in range(retries):
        try:
            # We use HttpClient to talk to the Docker container 'chromadb'
            client = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
            client.heartbeat() 
            print("✅ Backend connected to ChromaDB successfully.")
            
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
            return Chroma(
                client=client,
                collection_name="rag_documents",
                embedding_function=embeddings
            )
        except Exception as e:
            print(f"⏳ Waiting for Database... ({i+1}/{retries})")
            time.sleep(3)
    print("❌ Could not connect to ChromaDB. The app may crash.")
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

        # --- PDF PARSING LOGIC ---
        if filename.endswith(".pdf"):
            try:
                pdf_reader = PdfReader(io.BytesIO(content))
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\\n"
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid PDF file: {str(e)}")
        else:
            # Assume text/markdown
            text_content = content.decode("utf-8")

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="File is empty or could not be read")

        # Split text for better AI understanding
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.create_documents([text_content])
        
        # Save to Vector DB
        vector_store.add_documents(docs)
        
        return {"message": f"Processed {filename}", "chunks": len(docs), "xp_gained": 10}
        
    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    if not vector_store:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    try:
        # 1. Search the DB for relevant document chunks
        docs = vector_store.similarity_search(request.question, k=4)
        context = "\\n\\n".join([d.page_content for d in docs])
        
        # 2. Ask Gemini
        model = genai.GenerativeModel('gemini-pro')
        
        # System Prompt
        prompt = f"You are a helpful assistant. Answer the question based ONLY on the context below.\\n\\nContext:\\n{context}\\n\\nQuestion: {request.question}\\n\\nAnswer:"
        
        response = model.generate_content(prompt)
        
        return {
            "response": response.text,
            "context_used": context[:150] + "...",
            "xp_gained": 2
        }
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
"""

def get_frontend_dockerfile():
    return """FROM node:18-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
# 0.0.0.0 is required for Docker networking
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
"""

def get_vite_config():
    return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Listen on all IPs
    watch: { usePolling: true }, // Fix for Docker file changes not detecting
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})"""

def get_frontend_files():
    pkg = """{
  "name": "gemini-rag-ui",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": { "dev": "vite", "build": "vite build", "preview": "vite preview" },
  "dependencies": { "axios": "^1.6.0", "lucide-react": "^0.300.0", "react": "^18.2.0", "react-dom": "^18.2.0", "react-markdown": "^9.0.0", "zustand": "^4.5.0" },
  "devDependencies": { "@types/react": "^18.2.43", "@types/react-dom": "^18.2.17", "@vitejs/plugin-react": "^4.2.1", "autoprefixer": "^10.4.16", "postcss": "^8.4.32", "tailwindcss": "^3.4.0", "vite": "^5.0.8" }
}"""

    # Updated UI to handle PDF Uploads visualy
    app_jsx = """import { useState } from 'react'
import { create } from 'zustand'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { Terminal, Upload, Play, FileText } from 'lucide-react'

const useStore = create((set) => ({
  xp: 0,
  level: 1,
  addXp: (amount) => set((state) => ({ xp: state.xp + amount, level: Math.floor((state.xp + amount) / 100) + 1 }))
}))

export default function App() {
  const { xp, level, addXp } = useStore()
  const [query, setQuery] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    setUploadStatus('UPLOADING...')
    const formData = new FormData()
    formData.append('file', file)
    
    try {
        setLoading(true)
        const res = await axios.post('/api/upload', formData)
        addXp(res.data.xp_gained)
        setUploadStatus('SUCCESS: ' + file.name)
        alert('DOCUMENT EMBEDDED. AI CAN NOW READ IT.')
    } catch (err) { 
        console.error(err)
        setUploadStatus('FAILED. SEE CONSOLE.')
        alert('UPLOAD FAILED: ' + (err.response?.data?.detail || err.message))
    } finally { 
        setLoading(false) 
    }
  }

  const handleChat = async () => {
    if (!query) return
    const newHist = [...history, { role: 'user', content: query }]
    setHistory(newHist)
    setQuery('')
    try {
        setLoading(true)
        const res = await axios.post('/api/chat', { question: query })
        setHistory([...newHist, { role: 'bot', content: res.data.response }])
        addXp(res.data.xp_gained)
    } catch (err) { 
        setHistory([...newHist, { role: 'err', content: "ERROR: Connection refused. Is Docker running?" }]) 
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-black text-cyan-400 p-6 font-mono selection:bg-cyan-900">
      <div className="border-b border-cyan-800 pb-4 mb-6 flex justify-between items-center">
        <h1 className="text-xl font-bold tracking-widest flex items-center gap-2"><Terminal size={20}/> GEMINI_RAG_OS</h1>
        <div className="text-right">
            <div className="text-xs text-cyan-700">LEVEL {level}</div>
            <div className="w-32 h-2 bg-cyan-900 mt-1"><div className="h-full bg-cyan-400" style={{width: `${xp % 100}%`}}></div></div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-4 border border-cyan-800 rounded bg-cyan-900/10 h-fit">
            <h2 className="mb-4 text-sm font-bold flex gap-2 items-center"><Upload size={14}/> INGEST DOCUMENT</h2>
            <div className="border-2 border-dashed border-cyan-900 p-4 text-center hover:bg-cyan-900/20 transition-colors cursor-pointer relative">
                <input type="file" onChange={handleUpload} accept=".pdf,.txt,.md" className="absolute inset-0 opacity-0 cursor-pointer"/>
                <FileText className="mx-auto mb-2 opacity-50"/>
                <div className="text-[10px] text-cyan-600">DROP PDF / TXT HERE</div>
            </div>
            {uploadStatus && <div className="mt-2 text-[10px] text-center">{uploadStatus}</div>}
        </div>

        <div className="md:col-span-3 border border-cyan-800 rounded bg-cyan-900/5 h-[600px] flex flex-col relative overflow-hidden">
            <div className="flex-1 overflow-auto space-y-4 p-4">
                {history.length === 0 && <div className="text-cyan-800 text-center mt-20 opacity-50">SYSTEM ONLINE. UPLOAD PDF TO BEGIN.</div>}
                {history.map((m, i) => (
                    <div key={i} className={`p-3 text-sm ${m.role === 'user' ? 'text-right text-white' : 'text-cyan-400'}`}>
                        <div className="text-[10px] opacity-50 mb-1">{m.role.toUpperCase()}</div>
                        <ReactMarkdown>{m.content}</ReactMarkdown>
                    </div>
                ))}
            </div>
            <div className="p-4 border-t border-cyan-800 bg-black flex gap-2">
                <input value={query} onChange={e => setQuery(e.target.value)} 
                       onKeyDown={e => e.key === 'Enter' && handleChat()}
                       className="flex-1 bg-cyan-900/20 border border-cyan-800 p-2 text-cyan-100 outline-none focus:border-cyan-400 transition-colors" placeholder="Ask about the document..."/>
                <button onClick={handleChat} className="bg-cyan-700 hover:bg-cyan-600 text-black font-bold px-6 flex items-center justify-center"><Play size={16}/></button>
            </div>
        </div>
      </div>
    </div>
  )
}"""

    return {
        "frontend/package.json": pkg,
        "frontend/vite.config.js": get_vite_config(),
        "frontend/tailwind.config.js": "export default { content: ['./src/**/*.{js,jsx}'], theme: { extend: {} }, plugins: [] }",
        "frontend/postcss.config.js": "export default { plugins: { tailwindcss: {}, autoprefixer: {} } }",
        "frontend/index.html": "<!doctype html><html><head><title>Gemini RAG</title></head><body><div id='root'></div><script type='module' src='/src/main.jsx'></script></body></html>",
        "frontend/src/main.jsx": "import React from 'react'; import ReactDOM from 'react-dom/client'; import App from './App'; import './index.css'; ReactDOM.createRoot(document.getElementById('root')).render(<App />);",
        "frontend/src/App.jsx": app_jsx,
        "frontend/src/index.css": "@tailwind base; @tailwind components; @tailwind utilities;"
    }

# --- Execution ---

def main():
    print(f"🚀 INITIALIZING SETUP TARGET: {PROJECT_ROOT}")
    
    # 1. Create Directories
    for d in [".vscode", "backend", "frontend/src", "frontend/public", "docker"]:
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)

    # 2. Prepare Files
    files = {
        ".gitignore": get_gitignore(),
        ".env": "GEMINI_API_KEY=replace_with_your_key_here",
        "docker-compose.yml": get_docker_compose(),
        "backend/Dockerfile": get_backend_dockerfile(),
        "backend/requirements.txt": get_backend_requirements(),
        "backend/main.py": get_backend_main(),
        "frontend/Dockerfile": get_frontend_dockerfile(),
    }
    files.update(get_frontend_files())

    # 3. Write Files
    for path, content in files.items():
        full_path = PROJECT_ROOT / path
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            print(f"   -> Created {path}")
        except Exception as e:
            print(f"   ❌ Error creating {path}: {e}")

    # 4. Final instructions
    print("\n" + "="*60)
    print("✅ PROJECT GENERATION COMPLETE (PDF SUPPORT ENABLED)")
    print("="*60)
    print(f"📂 Project location: {PROJECT_ROOT}")
    print("⚠️  STEP 1: Open .env and paste your GEMINI_API_KEY")
    print("🚀 STEP 2: Run the following commands:")
    print(f"   cd {PROJECT_ROOT}")
    print("   docker-compose up --build")
    print("\n🌐 App URL: http://localhost:5173")
    print("="*60)

if __name__ == "__main__":
    main()