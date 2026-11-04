import logging
try:
    from langchain_ollama import ChatOllama
except ImportError:
    try:
        from langchain_community.chat_models.ollama import ChatOllama
    except ImportError:
        from langchain_community.chat_models import ChatOllama

from app.core.config import settings

logger = logging.getLogger(__name__)

def get_llm(model_name: str = None, temperature: float = 0.2, format_json: bool = False):
    """
    Factory function to instantiate local ChatOllama LLM.
    """
    target_model = model_name or settings.DEFAULT_MODEL
    logger.info(f"Instantiating ChatOllama with model: {target_model}")
    
    kwargs = {
        "base_url": settings.OLLAMA_BASE_URL,
        "model": target_model,
        "temperature": temperature,
    }
    
    if format_json:
        kwargs["format"] = "json"
        
    return ChatOllama(**kwargs)
