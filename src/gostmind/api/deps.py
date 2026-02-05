"""Зависимости для API-слоя.

Этот модуль является тонкой обёрткой над общими зависимостями из `gostmind.deps`,
чтобы избежать циклических импортов и явно разделить слой API и слой инфраструктуры.
"""

from typing import Any

from .. import deps as core_deps


async def get_llm_client() -> Any:
    """DI-обёртка для клиента LLM (Ollama)."""
    return await core_deps.get_llm_client()


async def get_vector_store() -> Any:
    """DI-обёртка для клиента векторного хранилища (Chroma)."""
    return await core_deps.get_vector_store()


async def get_redis() -> Any:
    """DI-обёртка для клиента Redis."""
    return await core_deps.get_redis()

