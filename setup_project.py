import os
import sys
import platform
from pathlib import Path

# --- Configuration ---
# Automatically detects Windows vs Mac path
if platform.system() == "Windows":
    # C:\Users\YourName\Documents\GitHub\Application
    REQUESTED_ROOT = Path.home() / "Documents" / "GitHub" / "Application"
else:
    # /Users/YourName/Documents/GitHub/Application
    REQUESTED_ROOT = Path.home() / "Documents" / "GitHub" / "Application"

CURRENT_ROOT = Path.cwd() / "gemini_rag_app"

def get_target_dir():
    try:
        # Try to create the requested path
        REQUESTED_ROOT.mkdir(parents=True, exist_ok=True)
        return REQUESTED_ROOT
    except Exception as e:
        print(f"⚠️ Could not write to {REQUESTED_ROOT} ({e})")
        print(f"   -> Falling back to: {CURRENT_ROOT}")
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
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""

def get_backend_requirements():
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
    # Using raw string r"..." to prevent escape sequence warnings
    return r"""import os
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
"""

def get_frontend_dockerfile():
    return """FROM node:18-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
"""

def get_vite_config():
    # Fixed the regex escape warning by using raw string r"..."
    return r"""import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    watch: { usePolling: true },
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
  const [status, setStatus] = useState('')

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setStatus('UPLOADING...')
    const formData = new FormData()
    formData.append('file', file)
    try {
        setLoading(true)
        const res = await axios.post('/api/upload', formData)
        addXp(res.data.xp_gained)
        setStatus('UPLOAD COMPLETE')
        alert('File Processed Successfully')
    } catch (err) { 
        setStatus('ERROR')
        alert('Upload Failed') 
    } finally { setLoading(false) }
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
        setHistory([...newHist, { role: 'err', content: "Connection Error" }]) 
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-black text-green-400 p-6 font-mono">
      <div className="border-b border-green-800 pb-4 mb-6 flex justify-between">
        <h1 className="text-xl font-bold flex gap-2"><Terminal/> GEMINI_RAG</h1>
        <div>LVL {level} | {xp} XP</div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-4 border border-green-800 rounded bg-green-900/10">
            <h2 className="mb-4 font-bold flex gap-2"><Upload size={16}/> INGEST</h2>
            <div className="border-2 border-dashed border-green-800 p-4 text-center cursor-pointer relative">
                <input type="file" onChange={handleUpload} className="absolute inset-0 opacity-0 cursor-pointer"/>
                <FileText className="mx-auto mb-2"/>
                <div className="text-xs">DROP PDF HERE</div>
            </div>
            <div className="mt-2 text-xs text-center">{status}</div>
        </div>

        <div className="md:col-span-3 border border-green-800 rounded h-[600px] flex flex-col">
            <div className="flex-1 overflow-auto p-4 space-y-4">
                {history.map((m, i) => (
                    <div key={i} className={`p-3 text-sm ${m.role === 'user' ? 'text-right text-white' : 'text-green-400'}`}>
                        <div className="text-[10px] opacity-50">{m.role}</div>
                        <ReactMarkdown>{m.content}</ReactMarkdown>
                    </div>
                ))}
            </div>
            <div className="p-4 border-t border-green-800 flex gap-2">
                <input value={query} onChange={e => setQuery(e.target.value)} 
                       onKeyDown={e => e.key === 'Enter' && handleChat()}
                       className="flex-1 bg-green-900/20 border border-green-800 p-2 outline-none" placeholder="Ask query..."/>
                <button onClick={handleChat} className="bg-green-700 text-black font-bold px-4">SEND</button>
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

def main():
    print(f"🚀 INITIALIZING at: {PROJECT_ROOT}")
    
    for d in [".vscode", "backend", "frontend/src", "frontend/public", "docker"]:
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)

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

    for path, content in files.items():
        try:
            with open(PROJECT_ROOT / path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            print(f"   -> Created {path}")
        except Exception as e:
            print(f"   ❌ Error {path}: {e}")

    print("\n" + "="*50)
    print("✅ SUCCESS!")
    print(f"📂 Project: {PROJECT_ROOT}")
    print("1. Open .env and add your GEMINI_API_KEY")
    print("2. cd " + str(PROJECT_ROOT))
    print("3. docker-compose up --build")
    print("="*50)

if __name__ == "__main__":
    main()