import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None
    CHROMA_DB_PATH: str = "./data/chroma"
    LOG_LEVEL: str = "INFO"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    class Config:
        env_file = ".env"

settings = Settings()
