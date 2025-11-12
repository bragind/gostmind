# src/gostmind/deps.py
from fastapi import Depends, Header, HTTPException, status
from typing import Annotated, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .infrastructure.database.session import get_session
from .infrastructure.vector_store.chroma_client import get_chroma_client
from .infrastructure.llm.openai_client import get_openai_client
from .infrastructure.cache.redis_client import get_redis_client


# Авторизация по API-ключу (MVP)
def verify_api_key(x_api_key: Annotated[str, Header(alias="X-API-Key")]) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


# DI для сессии БД
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


# DI для Redis
async def get_redis():
    return await get_redis_client()


# DI для Chroma
async def get_vector_store():
    return await get_chroma_client()


# DI для OpenAI
async def get_llm_client():
    return get_openai_client()