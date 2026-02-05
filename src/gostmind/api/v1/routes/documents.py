# src/gostmind/api/v1/routes/documents.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import structlog
from datetime import datetime

# Абсолютные импорты во избежание ошибок разрешения модулей
from gostmind.api.deps import get_llm_client, get_vector_store
from gostmind.domain.models.standard import Standard
from gostmind.domain.exceptions import VectorStoreError
from gostmind.application.document_processor import DocumentProcessor
from gostmind.infrastructure.vector_store.chroma_client import get_collection
from gostmind.infrastructure.vector_store.local_embedder import get_local_embedder
from gostmind.api.v1.schemas.document import DocumentUploadResponse, DocumentInfo

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    gost_number: str = None,
    llm_client=Depends(get_llm_client),
    vector_store=Depends(get_vector_store),
):
    """Загрузить и проиндексировать документ ГОСТ."""
    try:
        # Прочитать содержимое файла
        content = await file.read()
        text = content.decode("utf-8")

        # Определить номер ГОСТ из имени файла или параметра
        if not gost_number:
            # Попытаться извлечь из имени файла
            filename = file.filename or "unknown"
            gost_number = filename.replace(".txt", "").replace(".TXT", "")

        # Создать модель стандарта
        standard = Standard(
            number=gost_number,
            title=f"ГОСТ {gost_number}",
            content=text,
            file_path=file.filename,
        )

        # Обработать документ
        collection = get_collection()
        embedder = get_local_embedder()
        processor = DocumentProcessor(embedder=embedder, collection=collection)

        chunks_count = await processor.process_standard(standard)

        logger.info("Document uploaded and indexed", gost=gost_number, chunks=chunks_count)

        return DocumentUploadResponse(
            message="Документ успешно загружен и проиндексирован",
            gost_number=gost_number,
            chunks_count=chunks_count,
            indexed_at=datetime.utcnow(),
        )

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть в кодировке UTF-8",
        )
    except VectorStoreError as e:
        logger.error("Vector store error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при индексации документа",
        )
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )


@router.get("/documents", response_model=list[DocumentInfo])
async def list_documents(vector_store=Depends(get_vector_store)):
    """Получить список проиндексированных документов."""
    try:
        collection = get_collection()

        # Получить все документы (с ограничением для производительности)
        results = collection.get(limit=1000)

        # Извлечь уникальные ГОСТы из метаданных
        gosts = {}
        if results["metadatas"]:
            for metadata in results["metadatas"]:
                gost_number = metadata.get("gost_number", "Unknown")
                if gost_number not in gosts:
                    gosts[gost_number] = DocumentInfo(
                        gost_number=gost_number,
                        title=metadata.get("gost_title", f"ГОСТ {gost_number}"),
                        file_path=metadata.get("file_path"),
                        indexed_at=datetime.utcnow(),  # В реальности нужно хранить это в БД
                    )

        return list(gosts.values())

    except Exception as e:
        logger.error("Error listing documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении списка документов",
        )
