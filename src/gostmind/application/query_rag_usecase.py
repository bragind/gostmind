# src/gostmind/application/query_rag_usecase.py
import structlog
import chromadb

from ..domain.models.query import Query, QueryResult
from ..domain.exceptions import VectorStoreError, LLMError
from ..infrastructure.vector_store.local_embedder import LocalEmbedder
from ..infrastructure.llm.ollama_client import OllamaClient

logger = structlog.get_logger(__name__)


class QueryRAGUseCase:
    """Use case для обработки запросов с использованием RAG."""

    def __init__(
        self,
        llm_client: OllamaClient,
        embedder: LocalEmbedder,
        collection: chromadb.Collection,
        top_k: int = 5,
    ):
        self.llm_client = llm_client
        self.embedder = embedder
        self.collection = collection
        self.top_k = top_k

    async def execute(self, query: Query) -> QueryResult:
        """Выполнить RAG запрос."""
        try:
            # 1. Создать эмбеддинг запроса
            query_embedding = await self.embedder.embed_text(query.text)

            # 2. Найти релевантные документы в векторной БД
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=self.top_k,
                include=["documents", "metadatas", "distances"],
            )

            if not results["documents"] or not results["documents"][0]:
                logger.warning("No documents found for query", query=query.text)
                return QueryResult(
                    answer="Извините, не удалось найти релевантную информацию в базе ГОСТов.",
                    sources=[],
                    confidence=0.0,
                )

            # 3. Извлечь контекст из найденных документов
            documents = results["documents"][0]
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            distances = results["distances"][0] if results["distances"] else []

            # 4. Сформировать контекст для LLM
            context_parts = []
            sources = []
            for i, doc in enumerate(documents):
                gost_number = (
                    metadatas[i].get("gost_number", "Неизвестный ГОСТ")
                    if i < len(metadatas)
                    else "Неизвестный ГОСТ"
                )
                context_parts.append(f"[{gost_number}]\n{doc}")
                sources.append(gost_number)

            context = "\n\n---\n\n".join(context_parts)

            # 5. Сформировать промпт для LLM
            system_prompt = """Ты - интеллектуальный помощник инженера, специализирующийся на работе с ГОСТами.
Твоя задача - давать точные и полезные ответы на основе предоставленных фрагментов ГОСТов.
Отвечай на русском языке, будь точным и ссылайся на конкретные ГОСТы при ответе.
Если информации недостаточно, честно скажи об этом."""

            user_prompt = f"""Вопрос: {query.text}

Контекст из ГОСТов:
{context}

Ответь на вопрос, используя только информацию из предоставленного контекста. 
Если в контексте нет ответа, скажи об этом."""

            # 6. Получить ответ от LLM
            from ..config import settings

            # Ollama chat API возвращает поток, обрабатываем его
            try:
                response = await self.llm_client.chat(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens,
                )

                # Ollama может возвращать ответ в разных форматах
                # Проверяем несколько вариантов
                if isinstance(response, dict):
                    message = response.get("message", {})
                    if isinstance(message, dict):
                        answer = message.get("content", "")
                    else:
                        answer = str(message)
                else:
                    answer = str(response)

                # Если ответ пустой, используем generate API как fallback
                if not answer or answer.strip() == "":
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    answer = await self.llm_client.generate(
                        prompt=full_prompt,
                        temperature=settings.llm_temperature,
                        max_tokens=settings.llm_max_tokens,
                    )
            except Exception as e:
                logger.warning("Chat API failed, trying generate API", error=str(e))
                # Fallback на generate API
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                answer = await self.llm_client.generate(
                    prompt=full_prompt,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens,
                )

            # 7. Вычислить уверенность на основе расстояний
            avg_distance = sum(distances) / len(distances) if distances else 1.0
            confidence = max(
                0.0, min(1.0, 1.0 - avg_distance)
            )  # Преобразуем расстояние в уверенность

            logger.info(
                "Query processed successfully",
                query=query.text[:50],
                sources_count=len(sources),
                confidence=confidence,
            )

            return QueryResult(
                answer=answer,
                sources=list(set(sources)),  # Уникальные источники
                confidence=confidence,
            )

        except Exception as e:
            logger.error("Error processing query", query=query.text, error=str(e))
            if "chroma" in str(e).lower() or "vector" in str(e).lower():
                raise VectorStoreError(f"Ошибка работы с векторным хранилищем: {str(e)}")
            elif "ollama" in str(e).lower() or "llm" in str(e).lower() or "http" in str(e).lower():
                raise LLMError(f"Ошибка работы с LLM: {str(e)}")
            else:
                raise LLMError(f"Неожиданная ошибка при обработке запроса: {str(e)}")
