# src/gostmind/infrastructure/vector_store/embedder.py
# DEPRECATED: Этот файл оставлен для совместимости
# Используйте local_embedder.py для работы с Ollama
from typing import List
import structlog
from openai import AsyncOpenAI

logger = structlog.get_logger(__name__)


class Embedder:
    """Класс для создания эмбеддингов текста с помощью OpenAI."""
    
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.model = "text-embedding-3-small"  # Более дешевая модель для эмбеддингов
    
    async def embed_text(self, text: str) -> List[float]:
        """Создать эмбеддинг для одного текста."""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("Failed to create embedding", error=str(e))
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Создать эмбеддинги для батча текстов."""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error("Failed to create batch embeddings", error=str(e), count=len(texts))
            raise


def get_embedder(client) -> Embedder:
    """Фабрика для создания Embedder."""
    return Embedder(client)


async def get_embedder_async(client) -> Embedder:
    """Асинхронная фабрика для создания Embedder."""
    return Embedder(client)
