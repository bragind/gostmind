# src/gostmind/infrastructure/vector_store/local_embedder.py
from typing import List
import structlog
import httpx

from ...config import settings

logger = structlog.get_logger(__name__)


class LocalEmbedder:
    """Класс для создания эмбеддингов с помощью локальной модели (Ollama)."""

    def __init__(self, base_url: str, model: str, timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        logger.info("Local embedder initialized", base_url=base_url, model=model)

    async def embed_text(self, text: str) -> List[float]:
        """Создать эмбеддинг для одного текста."""
        try:
            payload = {"model": self.model, "prompt": text}

            response = await self.client.post(f"{self.base_url}/api/embeddings", json=payload)
            response.raise_for_status()
            result = response.json()
            embedding = result.get("embedding", [])

            if not embedding:
                raise ValueError("Empty embedding received")

            return embedding
        except Exception as e:
            logger.error("Failed to create embedding", error=str(e), text_length=len(text))
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Создать эмбеддинги для батча текстов."""
        # Ollama может не поддерживать батчи напрямую, поэтому обрабатываем последовательно
        # В production можно использовать пул воркеров для параллельной обработки
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings

    async def close(self):
        """Закрыть HTTP клиент."""
        await self.client.aclose()


def get_local_embedder() -> LocalEmbedder:
    """Фабрика для создания LocalEmbedder."""
    return LocalEmbedder(
        base_url=settings.embedding_base_url,
        model=settings.embedding_model,
        timeout=settings.llm_timeout,
    )
