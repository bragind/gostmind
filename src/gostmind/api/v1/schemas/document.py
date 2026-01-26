# src/gostmind/api/v1/schemas/document.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Схема ответа на загрузку документа."""
    message: str
    gost_number: str
    chunks_count: int
    indexed_at: datetime


class DocumentInfo(BaseModel):
    """Информация о документе."""
    gost_number: str
    title: str
    file_path: Optional[str] = None
    indexed_at: Optional[datetime] = None
