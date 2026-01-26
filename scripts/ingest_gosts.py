#!/usr/bin/env python3
"""
Скрипт для индексации ГОСТов из файлов в векторное хранилище.
"""

import asyncio
import sys
from pathlib import Path

# Добавить корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Импорты после изменения sys.path
from gostmind.domain.models.standard import Standard  # noqa: E402
from gostmind.application.document_processor import DocumentProcessor  # noqa: E402
from gostmind.infrastructure.vector_store.chroma_client import get_collection  # noqa: E402
from gostmind.infrastructure.vector_store.local_embedder import get_local_embedder  # noqa: E402
from gostmind.infrastructure.storage.file_ops import FileStorage  # noqa: E402
from gostmind.config import settings  # noqa: E402
import structlog  # noqa: E402

# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)

logger = structlog.get_logger(__name__)


def extract_gost_number(filename: str) -> str:
    """Извлечь номер ГОСТ из имени файла."""
    # Убрать расширение
    name = filename.replace(".txt", "").replace(".TXT", "")
    # Попытаться найти паттерн ГОСТ
    if "gost" in name.lower():
        parts = name.lower().split("gost")
        if len(parts) > 1:
            number = parts[1].strip().replace("_", " ").replace("-", " ")
            return f"ГОСТ {number}"
    return name


async def main():
    """Основная функция индексации."""
    logger.info("Starting GOST ingestion", documents_path=settings.documents_path)

    # Инициализация компонентов
    storage = FileStorage(settings.documents_path)
    embedder = get_local_embedder()
    collection = get_collection(settings.vector_store_collection)
    processor = DocumentProcessor(
        embedder=embedder,
        collection=collection,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    # Найти все файлы ГОСТов
    files = storage.list_files(".txt")
    logger.info("Found GOST files", count=len(files))

    if not files:
        logger.warning("No GOST files found", path=settings.documents_path)
        return

    # Обработать каждый файл
    standards = []
    for file_path in files:
        try:
            content = storage.read_file(file_path.name)
            if not content:
                logger.warning("Empty or unreadable file", file=file_path.name)
                continue

            gost_number = extract_gost_number(file_path.name)
            standard = Standard(
                number=gost_number,
                title=f"ГОСТ {gost_number}",
                content=content,
                file_path=str(file_path),
            )
            standards.append(standard)
            logger.info(
                "Prepared standard for indexing", gost=gost_number, file=file_path.name
            )
        except Exception as e:
            logger.error("Error reading file", file=file_path.name, error=str(e))

    # Индексировать батч
    if standards:
        logger.info("Starting batch indexing", count=len(standards))
        results = await processor.process_batch(standards)
        logger.info(
            "Batch indexing completed",
            total=results["total"],
            success=results["success"],
            failed=results["failed"],
            total_chunks=results["total_chunks"],
        )
    else:
        logger.warning("No standards to index")


if __name__ == "__main__":
    asyncio.run(main())
