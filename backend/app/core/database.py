import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

class ChromaDBManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection = None
    
    def get_or_create_collection(self, name: str = "documents"):
        if self.collection is None:
            self.collection = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collection

chroma_manager = ChromaDBManager()
