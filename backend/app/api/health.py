import httpx
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """
    Health check verifying backend server and local Ollama daemon connection.
    """
    ollama_online = False
    models_available = []
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                ollama_online = True
                data = resp.json()
                models_available = [m.get("name") for m in data.get("models", [])]
    except Exception:
        ollama_online = False

    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ollama": {
            "online": ollama_online,
            "base_url": settings.OLLAMA_BASE_URL,
            "available_models": models_available
        }
    }
