# src/gostmind/api/v1/schemas/query.py
from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """Схема запроса пользователя."""

    query: str = Field(..., description="Текст запроса", min_length=1, max_length=1000)
    user_id: Optional[str] = Field(None, description="Идентификатор пользователя")


class QueryResponse(BaseModel):
    """Схема ответа на запрос."""

    answer: str = Field(..., description="Ответ на запрос")
    sources: List[str] = Field(..., description="Список ГОСТов, использованных для ответа")
    confidence: float = Field(..., description="Уверенность в ответе (0-1)", ge=0.0, le=1.0)
    query_id: Optional[str] = Field(None, description="Идентификатор запроса")
