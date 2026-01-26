# src/gostmind/infrastructure/vector_store/chroma_client.py
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import Optional
import structlog

from ...config import settings

logger = structlog.get_logger(__name__)

_chroma_client: Optional[chromadb.ClientAPI] = None
_collection: Optional[chromadb.Collection] = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Получить клиент ChromaDB (singleton)."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        logger.info("ChromaDB client initialized", path=settings.chroma_path)
    return _chroma_client


def get_collection(name: str = "gosts") -> chromadb.Collection:
    """Получить коллекцию документов ГОСТ."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        try:
            _collection = client.get_collection(name=name)
            logger.info("ChromaDB collection loaded", collection=name)
        except Exception:
            _collection = client.create_collection(
                name=name, metadata={"description": "ГОСТ документы для RAG поиска"}
            )
            logger.info("ChromaDB collection created", collection=name)
    return _collection


def reset_collection(name: str = "gosts") -> None:
    """Сбросить коллекцию (для тестов или переиндексации)."""
    global _collection
    client = get_chroma_client()
    try:
        client.delete_collection(name=name)
        logger.info("ChromaDB collection deleted", collection=name)
    except Exception:
        pass
    _collection = None
    get_collection(name=name)
