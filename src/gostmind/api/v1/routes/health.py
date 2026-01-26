# src/gostmind/api/v1/routes/health.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import structlog

from ...deps import get_redis, get_vector_store
from ...infrastructure.vector_store.chroma_client import get_chroma_client

logger = structlog.get_logger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Схема ответа health check."""

    status: str
    version: str
    services: dict


@router.get("/health", response_model=HealthResponse)
async def health_check(
    redis=Depends(get_redis), vector_store=Depends(get_vector_store)
):
    """Проверка здоровья сервиса и зависимостей."""
    services_status = {}

    # Проверка Redis
    try:
        await redis.ping()
        services_status["redis"] = "healthy"
    except Exception as e:
        logger.warning("Redis health check failed", error=str(e))
        services_status["redis"] = "unhealthy"

    # Проверка ChromaDB
    try:
        client = get_chroma_client()
        # Простая проверка - попытка получить список коллекций
        client.list_collections()
        services_status["chromadb"] = "healthy"
    except Exception as e:
        logger.warning("ChromaDB health check failed", error=str(e))
        services_status["chromadb"] = "unhealthy"

    # Общий статус
    all_healthy = all(s == "healthy" for s in services_status.values())
    overall_status = "healthy" if all_healthy else "degraded"

    return HealthResponse(
        status=overall_status, version="0.1.0", services=services_status
    )
