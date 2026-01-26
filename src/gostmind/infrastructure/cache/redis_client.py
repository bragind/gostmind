# src/gostmind/infrastructure/cache/redis_client.py
from typing import Optional
import redis.asyncio as aioredis
import structlog
import json

from ...config import settings

logger = structlog.get_logger(__name__)

_redis_client: Optional[aioredis.Redis] = None


async def get_redis_client() -> aioredis.Redis:
    """Получить клиент Redis (singleton)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            str(settings.redis_url),
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("Redis client initialized", url=str(settings.redis_url))
    return _redis_client


async def close_redis_client() -> None:
    """Закрыть соединение с Redis."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis client closed")


class CacheService:
    """Сервис для работы с кэшем."""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[str]:
        """Получить значение из кэша."""
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.warning("Cache get error", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Установить значение в кэш с TTL."""
        try:
            await self.redis.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.warning("Cache set error", key=key, error=str(e))
            return False
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Получить JSON из кэша."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(self, key: str, value: dict, ttl: int = 3600) -> bool:
        """Установить JSON в кэш."""
        try:
            json_str = json.dumps(value, ensure_ascii=False)
            return await self.set(key, json_str, ttl)
        except Exception as e:
            logger.warning("Cache set_json error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Удалить ключ из кэша."""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning("Cache delete error", key=key, error=str(e))
            return False
