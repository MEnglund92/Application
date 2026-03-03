from fastapi import UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from app.core.config import settings
from app.models.schemas import SearchResult
import chromadb
import uuid
from pypdf import PdfReader
import logging
import os

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, collection):
        self.collection = collection
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        ) if settings.OPENAI_API_KEY else None
        
        # Fallback to simple text processing if no embeddings available
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    async def process_document(self, file: UploadFile) -> int:
        """Process uploaded document and store in vector DB"""
        content = await self._extract_text(file)
        chunks = self.text_splitter.split_text(content)
        
        documents_processed = 0
        
        for i, chunk in enumerate(chunks):
            try:
                if self.embeddings:
                    # Use OpenAI embeddings
                    embedding = self.embeddings.embed_query(chunk)
                    self.collection.add(
                        ids=[f"{file.filename}_{i}_{uuid.uuid4()}"],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[{
                            "source": file.filename,
                            "chunk": i,
                            "type": "document"
                        }]
                    )
                else:
                    # Store without embeddings for now
                    self.collection.add(
                        ids=[f"{file.filename}_{i}_{uuid.uuid4()}"],
                        documents=[chunk],
                        metadatas=[{
                            "source": file.filename,
                            "chunk": i,
                            "type": "document"
                        }]
                    )
                documents_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {str(e)}")
                continue
        
        return documents_processed
    
    async def _extract_text(self, file: UploadFile) -> str:
        """Extract text from uploaded file"""
        content = await file.read()
        
        if file.filename.lower().endswith('.pdf'):
            try:
                from io import BytesIO
                pdf_reader = PdfReader(BytesIO(content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            except Exception as e:
                logger.error(f"PDF processing error: {str(e)}")
                raise Exception("Failed to process PDF file")
        
        elif file.filename.lower().endswith('.txt'):
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                return content.decode('latin-1')
        
        else:
            raise ValueError("Unsupported file type")
    
    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Search for relevant documents"""
        try:
            if self.embeddings:
                query_embedding = self.embeddings.embed_query(query)
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=max_results
                )
            else:
                # Simple text search fallback
                results = self.collection.query(
                    query_texts=[query],
                    n_results=max_results
                )
            
            search_results = []
            for i in range(len(results['documents'][0])):
                doc = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i] if 'distances' in results else 0.0
                
                search_results.append(SearchResult(
                    content=doc,
                    source=metadata.get('source', 'Unknown'),
                    page=metadata.get('chunk'),
                    score=1 - distance  # Convert distance to similarity score
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")
    
    def get_vector_db_size(self) -> float:
        """Get size of vector database in MB"""
        try:
            db_path = settings.CHROMA_DB_PATH
            if os.path.exists(db_path):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(db_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(filepath)
                return total_size / (1024 * 1024)  # Convert to MB
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating DB size: {str(e)}")
            return 0.0
