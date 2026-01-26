# src/gostmind/application/document_processor.py
from typing import List, Optional
import structlog
import chromadb
from openai import AsyncOpenAI

from ..domain.models.standard import Standard
from ..domain.exceptions import VectorStoreError
from ..infrastructure.vector_store.chroma_client import get_collection
from ..infrastructure.vector_store.embedder import Embedder

logger = structlog.get_logger(__name__)


class DocumentProcessor:
    """Класс для обработки и индексации документов ГОСТ."""
    
    def __init__(
        self,
        embedder: Embedder,
        collection: chromadb.Collection,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.embedder = embedder
        self.collection = collection
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def _chunk_text(self, text: str, gost_number: str) -> List[dict]:
        """Разбить текст на чанки для индексации."""
        chunks = []
        words = text.split()
        
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 для пробела
            
            if current_length + word_length > self.chunk_size and current_chunk:
                # Сохранить текущий чанк
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "gost_number": gost_number
                })
                
                # Начать новый чанк с перекрытием
                overlap_words = current_chunk[-self.chunk_overlap // 10:]  # Примерное перекрытие
                current_chunk = overlap_words + [word]
                current_length = sum(len(w) + 1 for w in current_chunk)
            else:
                current_chunk.append(word)
                current_length += word_length
        
        # Добавить последний чанк
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "gost_number": gost_number
            })
        
        return chunks
    
    async def process_standard(self, standard: Standard) -> int:
        """Обработать и проиндексировать ГОСТ."""
        try:
            # Разбить на чанки
            chunks = self._chunk_text(standard.content, standard.number)
            
            if not chunks:
                logger.warning("No chunks created", gost=standard.number)
                return 0
            
            # Создать эмбеддинги для всех чанков
            texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.embedder.embed_batch(texts)
            
            # Подготовить данные для добавления в ChromaDB
            ids = [f"{standard.number}_{i}" for i in range(len(chunks))]
            documents = texts
            metadatas = [
                {
                    "gost_number": standard.number,
                    "gost_title": standard.title,
                    "chunk_index": i,
                    "file_path": standard.file_path or ""
                }
                for i in range(len(chunks))
            ]
            
            # Добавить в коллекцию
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(
                "Standard indexed successfully",
                gost=standard.number,
                chunks_count=len(chunks)
            )
            
            return len(chunks)
            
        except Exception as e:
            logger.error("Error processing standard", gost=standard.number, error=str(e))
            raise VectorStoreError(f"Ошибка при индексации ГОСТ: {str(e)}")
    
    async def process_batch(self, standards: List[Standard]) -> dict:
        """Обработать батч ГОСТов."""
        results = {
            "total": len(standards),
            "success": 0,
            "failed": 0,
            "total_chunks": 0
        }
        
        for standard in standards:
            try:
                chunks_count = await self.process_standard(standard)
                results["success"] += 1
                results["total_chunks"] += chunks_count
            except Exception as e:
                results["failed"] += 1
                logger.error("Failed to process standard", gost=standard.number, error=str(e))
        
        return results
