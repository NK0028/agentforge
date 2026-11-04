import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgentForge API"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # Ollama Local Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen2.5-coder")
    
    # Workspace & Sandbox Root
    WORKSPACE_DIR: str = os.getenv("WORKSPACE_DIR", os.path.abspath("./workspace"))

    class Config:
        case_sensitive = True

settings = Settings()
