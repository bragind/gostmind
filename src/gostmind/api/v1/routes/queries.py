# src/gostmind/api/v1/routes/queries.py
from fastapi import APIRouter, Depends, HTTPException, status
import structlog
import uuid

from ...deps import get_llm_client, get_vector_store, get_redis
from ...domain.models.query import Query
from ...domain.exceptions import VectorStoreError, LLMError, RateLimitExceededError
from ...application.query_rag_usecase import QueryRAGUseCase
from ...infrastructure.vector_store.chroma_client import get_collection
from ...infrastructure.vector_store.local_embedder import get_local_embedder
from ...infrastructure.cache.redis_client import CacheService
from ...config import settings
from ..schemas.query import QueryRequest, QueryResponse

logger = structlog.get_logger(__name__)
router = APIRouter()


async def check_rate_limit(user_id: str, cache_service: CacheService) -> None:
    """Проверить rate limit для пользователя."""
    key = f"rate_limit:{user_id}"
    current = await cache_service.get(key)

    if current is None:
        await cache_service.set(key, "1", ttl=settings.rate_limit_window)
        return

    count = int(current)
    if count >= settings.rate_limit_requests:
        raise RateLimitExceededError(
            f"Превышен лимит запросов: {settings.rate_limit_requests} в {settings.rate_limit_window} секунд"
        )

    await cache_service.set(key, str(count + 1), ttl=settings.rate_limit_window)


@router.post("/queries", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def process_query(
    request: QueryRequest,
    llm_client=Depends(get_llm_client),
    vector_store=Depends(get_vector_store),
    redis=Depends(get_redis),
):
    """Обработать запрос пользователя с использованием RAG."""
    query_id = str(uuid.uuid4())
    user_id = request.user_id or "anonymous"

    try:
        # Проверка rate limit
        cache_service = CacheService(redis)
        await check_rate_limit(user_id, cache_service)

        # Проверка кэша
        cache_key = f"query:{hash(request.query)}"
        cached_result = await cache_service.get_json(cache_key)
        if cached_result:
            logger.info("Query result from cache", query_id=query_id)
            return QueryResponse(**cached_result, query_id=query_id)

        # Создание зависимостей
        collection = get_collection()
        embedder = get_local_embedder()

        # Создание use case
        use_case = QueryRAGUseCase(llm_client=llm_client, embedder=embedder, collection=collection)

        # Выполнение запроса
        domain_query = Query(text=request.query, user_id=user_id)

        result = await use_case.execute(domain_query)

        # Сохранение в кэш
        response_data = {
            "answer": result.answer,
            "sources": result.sources,
            "confidence": result.confidence,
        }
        await cache_service.set_json(cache_key, response_data, ttl=3600)

        return QueryResponse(
            answer=result.answer,
            sources=result.sources,
            confidence=result.confidence,
            query_id=query_id,
        )

    except RateLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except VectorStoreError as e:
        logger.error("Vector store error", error=str(e), query_id=query_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка работы с векторным хранилищем",
        )
    except LLMError as e:
        logger.error("LLM error", error=str(e), query_id=query_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка работы с языковой моделью",
        )
    except Exception as e:
        logger.error("Unexpected error", error=str(e), query_id=query_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )
