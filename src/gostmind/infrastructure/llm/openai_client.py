# src/gostmind/infrastructure/llm/openai_client.py
from typing import Optional
from openai import AsyncOpenAI
import structlog

from ...config import settings

logger = structlog.get_logger(__name__)

_openai_client: Optional[AsyncOpenAI] = None


def get_openai_client() -> AsyncOpenAI:
    """Получить клиент OpenAI (singleton)."""
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        logger.info("OpenAI client initialized", model=settings.openai_model)
    return _openai_client
