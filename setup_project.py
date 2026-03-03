#!/usr/bin/env python3
import os
import subprocess
import json
from pathlib import Path

def setup_project():
    # Define the root path
    root_path = Path("/Users/mattias/Documents/GitHub/Application")
    
    # Pre-flight checks
    print("🔍 Running pre-flight checks...")
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker is installed")
    except subprocess.CalledProcessError:
        print("❌ Docker is not installed or not running")
        return
    
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✅ Node.js is installed")
    except subprocess.CalledProcessError:
        print("❌ Node.js is not installed")
        return
    
    # Create project structure
    print("🏗️ Creating project structure...")
    directories = [
        ".vscode",
        "backend",
        "frontend",
        "docker",
        "frontend/src",
        "frontend/src/components",
        "frontend/public"
    ]
    
    for dir_name in directories:
        (root_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    # File contents dictionary
    files = {
        ".gitignore": """# Dependencies
node_modules/
__pycache__/
.env
.DS_Store
dist/
coverage/
.pytest_cache/

# IDE
.vscode/settings.json
.idea/

# Docker
docker-compose.override.yml
""",
        
        ".vscode/settings.json": """{
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "files.associations": {
        "*.jsx": "javascriptreact",
        "*.js": "javascriptreact"
    },
    "emmet.includeLanguages": {
        "javascript": "javascriptreact"
    }
}
""",
        
        ".vscode/launch.json": """{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Remote Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/backend",
                    "remoteRoot": "/app"
                }
            ],
            "justMyCode": false
        }
    ]
}
""",
        
        ".env": "GEMINI_API_KEY=replace_with_your_key_here\n",
        
        "docker-compose.yml": """version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - chroma_data:/chroma/chroma
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    networks:
      - app-network
    depends_on:
      - chromadb

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - app-network
    depends_on:
      - backend

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    networks:
      - app-network

volumes:
  chroma_data:

networks:
  app-network:
    driver: bridge
""",
        
        "backend/requirements.txt": """fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
langchain==0.0.350
langchain-google-genai==0.0.5
chromadb==0.4.15
python-dotenv==1.0.0
pydantic==2.5.0
""",
        
        "backend/Dockerfile": """FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
""",
        
        "backend/main.py": """from fastapi import FastAPI, HTTPException, UploadFile, File
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
    prompt = f"Context: {context}\\n\\nQuestion: {request.question}\\n\\nAnswer based on the context provided:"
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
    prompt = f"Generate a multiple choice question based on this text: {context}\\n\\nReturn in format:\\nQuestion: [question]\\nA. [option1]\\nB. [option2]\\nC. [option3]\\nD. [option4]\\nCorrect: [A/B/C/D]"
    response = llm([HumanMessage(content=prompt)])
    
    # Parse response (simplified parsing)
    lines = response.content.split('\\n')
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
""",
        
        "frontend/package.json": """{
  "name": "rag-gamified-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.294.0",
    "axios": "^1.6.2",
    "zustand": "^4.4.7",
    "react-markdown": "^9.0.1",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.55.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
""",
        
        "frontend/Dockerfile": """FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
""",
        
        "frontend/vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
""",
        
        "frontend/tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-blue': '#00ffff',
        'cyber-pink': '#ff00ff',
        'cyber-green': '#00ff00',
        'dark-bg': '#0a0a0f',
      },
      animation: {
        'pulse-glow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        slideUp: {
          'from': { transform: 'translateY(100%)', opacity: '0' },
          'to': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
""",
        
        "frontend/postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""",
        
        "frontend/index.html": """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>RAG Gamified Platform</title>
  </head>
  <body class="bg-dark-bg text-white">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""",
        
        "frontend/src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { Toaster } from 'react-hot-toast'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
    <Toaster position="top-right" />
  </React.StrictMode>,
)
""",
        
        "frontend/src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    font-family: 'Courier New', monospace;
    background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
  }
}

@layer components {
  .cyber-border {
    border: 2px solid;
    border-image: linear-gradient(45deg, #00ffff, #ff00ff) 1;
  }
  
  .xp-bar {
    background: linear-gradient(90deg, #00ff00 0%, #00ffff 100%);
    transition: width 0.5s ease-out;
  }
}
""",
        
        "frontend/src/App.jsx": """import React, { useState, useEffect } from 'react'
import { Upload, MessageCircle, Trophy, FileText, Zap } from 'lucide-react'
import { useStore } from './store'
import { uploadFile, chat, generateQuiz, getStats } from './api'
import ChatInterface from './components/ChatInterface'
import QuizInterface from './components/QuizInterface'
import toast from 'react-hot-toast'

function App() {
  const { xp, level, addXP } = useStore()
  const [activeTab, setActiveTab] = useState('upload')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  useEffect(() => {
    // Fetch initial stats
    getStats().catch(err => {
      if (err.response?.status === 500) {
        toast.error('Please set GEMINI_API_KEY in .env file')
      }
    })
  }, [])

  const handleFileUpload = async (e) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await uploadFile(formData)
      addXP(response.xp_gained)
      toast.success(`✨ +${response.xp_gained} XP gained!`)
      setFile(null)
      setUploadProgress(100)
      setTimeout(() => setUploadProgress(0), 1000)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const xpPercentage = (xp / 100) * 100

  return (
    <div className="min-h-screen p-8">
      {/* Header with XP Bar */}
      <header className="mb-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-cyber-blue to-cyber-pink bg-clip-text text-transparent">
            RAG Gamified Platform
          </h1>
          
          {/* XP System */}
          <div className="cyber-border rounded-lg p-4 bg-black/50 backdrop-blur">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-cyber-green" />
                <span className="font-bold">Level {level}</span>
              </div>
              <span className="text-cyber-green">{xp}/100 XP</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-3 overflow-hidden">
              <div 
                className="xp-bar h-full rounded-full"
                style={{ width: `${xpPercentage}%` }}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-6xl mx-auto mb-6">
        <div className="flex gap-4 border-b border-cyber-blue/30">
          {[
            { id: 'upload', label: 'Upload', icon: Upload },
            { id: 'chat', label: 'Chat', icon: MessageCircle },
            { id: 'quiz', label: 'Quiz', icon: Trophy },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center gap-2 px-4 py-2 font-semibold transition-all ${
                activeTab === id
                  ? 'text-cyber-blue border-b-2 border-cyber-blue'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-6xl mx-auto">
        {activeTab === 'upload' && (
          <div className="cyber-border rounded-lg p-8 bg-black/50 backdrop-blur">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <FileText className="w-6 h-6 text-cyber-blue" />
              Upload Documents
            </h2>
            
            <form onSubmit={handleFileUpload} className="space-y-6">
              <div className="border-2 border-dashed border-cyber-pink/50 rounded-lg p-8 text-center hover:border-cyber-pink transition-colors">
                <input
                  type="file"
                  onChange={(e) => setFile(e.target.files[0])}
                  accept=".pdf,.txt"
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer block"
                >
                  <Upload className="w-12 h-12 mx-auto mb-4 text-cyber-pink" />
                  <p className="text-lg mb-2">Click to upload or drag and drop</p>
                  <p className="text-gray-400">PDF or TXT files only</p>
                  {file && (
                    <p className="mt-4 text-cyber-green">
                      Selected: {file.name}
                    </p>
                  )}
                </label>
              </div>

              {uploadProgress > 0 && (
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div 
                    className="bg-cyber-blue h-full rounded-full transition-all"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={!file || loading}
                className="w-full py-3 bg-gradient-to-r from-cyber-blue to-cyber-pink font-bold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-80 transition-opacity"
              >
                {loading ? 'Uploading...' : 'Upload & Gain 10 XP'}
              </button>
            </form>
          </div>
        )}

        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'quiz' && <QuizInterface />}
      </div>
    </div>
  )
}

export default App
""",
        
        "frontend/src/store.js": """import { create } from 'zustand'

export const useStore = create((set) => ({
  xp: 0,
  level: 1,
  addXP: (amount) => set((state) => {
    const newXp = state.xp + amount
    const newLevel = state.level + Math.floor(newXp / 100)
    return {
      xp: newXp % 100,
      level: newLevel,
    }
  }),
}))
""",
        
        "frontend/src/api.js": """import axios from 'axios'
import toast from 'react-hot-toast'

const api = axios.create({
  baseURL: '/api',
})

export const uploadFile = async (formData) => {
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const chat = async (question) => {
  const response = await api.post('/chat', { question })
  return response.data
}

export const generateQuiz = async () => {
  const response = await api.get('/quiz')
  return response.data
}

export const getStats = async () => {
  const response = await api.get('/stats')
  return response.data
}
""",
        
        "frontend/src/components/ChatInterface.jsx": """import React, { useState } from 'react'
import { Send, Bot, User } from 'lucide-react'
import { chat } from '../api'
import { useStore } from '../store'
import toast from 'react-hot-toast'

export default function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const { addXP } = useStore()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await chat(input)
      const botMessage = { role: 'bot', content: response.response }
      setMessages(prev => [...prev, botMessage])
      addXP(response.xp_gained)
      toast.success(`✨ +${response.xp_gained} XP gained!`)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Chat failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="cyber-border rounded-lg p-6 bg-black/50 backdrop-blur">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
        <Bot className="w-6 h-6 text-cyber-blue" />
        AI Chat Assistant
      </h2>

      <div className="h-96 overflow-y-auto mb-4 space-y-4 p-4 bg-gray-900/50 rounded-lg">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            Start a conversation with your documents!
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-3 ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'bot' && <Bot className="w-8 h-8 text-cyber-blue flex-shrink-0" />}
              <div
                className={`max-w-xs p-3 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-cyber-blue to-cyber-pink'
                    : 'bg-gray-800'
                }`}
              >
                {msg.content}
              </div>
              {msg.role === 'user' && <User className="w-8 h-8 text-cyber-green flex-shrink-0" />}
            </div>
          ))
        )}
        {loading && (
          <div className="flex items-center gap-2 text-gray-400">
            <Bot className="w-8 h-8" />
            <span>Thinking...</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your documents..."
          className="flex-1 px-4 py-3 bg-gray-900 border border-cyber-blue/50 rounded-lg focus:outline-none focus:border-cyber-blue"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-gradient-to-r from-cyber-blue to-cyber-pink rounded-lg disabled:opacity-50 hover:opacity-80 transition-opacity"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  )
}
""",
        
        "frontend/src/components/QuizInterface.jsx": """import React, { useState, useEffect } from 'react'
import { Trophy, RotateCcw } from 'lucide-react'
import { generateQuiz } from '../api'
import { useStore } from '../store'
import toast from 'react-hot-toast'

export default function QuizInterface() {
  const [quiz, setQuiz] = useState(null)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [showResult, setShowResult] = useState(false)
  const [loading, setLoading] = useState(false)
  const { addXP } = useStore()

  const loadQuiz = async () => {
    setLoading(true)
    try {
      const newQuiz = await generateQuiz()
      setQuiz(newQuiz)
      setSelectedAnswer(null)
      setShowResult(false)
      addXP(newQuiz.xp_gained)
      toast.success(`✨ +${newQuiz.xp_gained} XP for generating quiz!`)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate quiz')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadQuiz()
  }, [])

  const handleSubmit = () => {
    if (selectedAnswer === null) return
    setShowResult(true)
    if (selectedAnswer === quiz.correct_answer) {
      toast.success('🎉 Correct Answer! +20 XP')
      addXP(20)
    } else {
      toast.error('❌ Incorrect. Try again!')
    }
  }

  return (
    <div className="cyber-border rounded-lg p-6 bg-black/50 backdrop-blur">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-3">
          <Trophy className="w-6 h-6 text-cyber-pink" />
          Knowledge Quiz
        </h2>
        <button
          onClick={loadQuiz}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyber-blue to-cyber-pink rounded-lg disabled:opacity-50 hover:opacity-80 transition-opacity"
        >
          <RotateCcw className="w-4 h-4" />
          {loading ? 'Loading...' : 'New Quiz'}
        </button>
      </div>

      {quiz ? (
        <div className="space-y-6">
          <div className="p-6 bg-gray-900/50 rounded-lg">
            <h3 className="text-xl font-semibold mb-4">{quiz.question}</h3>
            
            <div className="space-y-3">
              {quiz.options.map((option, idx) => (
                <button
                  key={idx}
                  onClick={() => !showResult && setSelectedAnswer(idx)}
                  disabled={showResult}
                  className={`w-full text-left p-4 rounded-lg border transition-all ${
                    showResult
                      ? idx === quiz.correct_answer
                        ? 'bg-green-900/50 border-green-500'
                        : selectedAnswer === idx
                        ? 'bg-red-900/50 border-red-500'
                        : 'bg-gray-800/50 border-gray-700'
                      : selectedAnswer === idx
                      ? 'bg-cyber-blue/20 border-cyber-blue'
                      : 'bg-gray-900/30 border-gray-700 hover:border-cyber-blue/50'
                  }`}
                >
                  <span className="font-semibold mr-3">{String.fromCharCode(65 + idx)}.</span>
                  {option}
                </button>
              ))}
            </div>
          </div>

          {!showResult && selectedAnswer !== null && (
            <button
              onClick={handleSubmit}
              className="w-full py-3 bg-gradient-to-r from-cyber-green to-cyber-blue font-bold rounded-lg hover:opacity-80 transition-opacity"
            >
              Submit Answer
            </button>
          )}

          {showResult && (
            <div className="p-4 bg-gray-900/50 rounded-lg text-center">
              <p className="text-lg">
                {selectedAnswer === quiz.correct_answer ? (
                  <span className="text-green-400">🎉 Correct! Well done!</span>
                ) : (
                  <span className="text-red-400">
                    ❌ Incorrect. The correct answer was {String.fromCharCode(65 + quiz.correct_answer)}
                  </span>
                )}
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          Loading quiz...
        </div>
      )}
    </div>
  )
}
"""
    }
    
    # Write all files
    print("📝 Generating project files...")
    for file_path, content in files.items():
        full_path = root_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Finalize setup
    finalize_setup(root_path)

def finalize_setup(root_path):
    print("\n🔧 Finalizing setup...")
    
    # Change to frontend directory and run npm install
    frontend_path = root_path / "frontend"
    print("📦 Installing frontend dependencies...")
    try:
        subprocess.run(["npm", "install"], cwd=frontend_path, check=True, capture_output=True)
        print("✅ Frontend dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        print("Please run 'npm install' manually in the frontend directory")
    
    # Print final instructions
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print(f"✅ Project created at {root_path}")
    print("\n⚠️  ACTION REQUIRED:")
    print("   Open .env and paste your Gemini API Key")
    print(f"   Path: {root_path}/.env")
    print("\n▶️  TO START THE APPLICATION:")
    print(f"   cd {root_path}")
    print("   docker-compose up --build")
    print("\n🌐 Once running, access the app at:")
    print("   http://localhost:5173")
    print("\n🔧 API Documentation:")
    print("   http://localhost:8000/docs")
    print("="*60)

if __name__ == "__main__":
    setup_project()
