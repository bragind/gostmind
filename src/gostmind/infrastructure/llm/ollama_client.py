# src/gostmind/infrastructure/llm/ollama_client.py
from typing import Optional, List, Dict, Any
import httpx
import structlog

from ...config import settings

logger = structlog.get_logger(__name__)


class OllamaClient:
    """Клиент для работы с локальной LLM через Ollama API."""

    def __init__(self, base_url: str, model: str, timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        logger.info("Ollama client initialized", base_url=base_url, model=model)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Отправить запрос на генерацию текста через chat API."""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": stream,
                "options": {"temperature": temperature, **kwargs},
            }

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            response = await self.client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()

            if stream:
                # Для streaming нужно обрабатывать поток
                # Пока возвращаем последний чанк
                result = {"message": {"content": ""}}
                async for line in response.aiter_lines():
                    if line:
                        import json

                        chunk = json.loads(line)
                        if "message" in chunk:
                            result["message"]["content"] += chunk["message"].get(
                                "content", ""
                            )
                return result
            else:
                return response.json()
        except httpx.HTTPError as e:
            logger.error("Ollama API error", error=str(e))
            raise

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Генерировать текст по промпту."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "options": {"temperature": temperature, **kwargs},
            }

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            response = await self.client.post(
                f"{self.base_url}/api/generate", json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except httpx.HTTPError as e:
            logger.error("Ollama generate error", error=str(e))
            raise

    async def embeddings(self, text: str) -> List[float]:
        """Получить эмбеддинг для текста."""
        try:
            payload = {"model": self.model, "prompt": text}

            response = await self.client.post(
                f"{self.base_url}/api/embeddings", json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])
        except httpx.HTTPError as e:
            logger.error("Ollama embeddings error", error=str(e))
            raise

    async def close(self):
        """Закрыть HTTP клиент."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Получить клиент Ollama (singleton)."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient(
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout=settings.llm_timeout,
        )
        logger.info("Ollama client created", model=settings.llm_model)
    return _ollama_client


async def close_ollama_client() -> None:
    """Закрыть соединение с Ollama."""
    global _ollama_client
    if _ollama_client is not None:
        await _ollama_client.close()
        _ollama_client = None
        logger.info("Ollama client closed")
