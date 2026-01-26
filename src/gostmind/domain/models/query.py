# src/gostmind/domain/models/query.py
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Query:
    """Доменная модель запроса пользователя."""

    text: str
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class QueryResult:
    """Результат обработки запроса."""

    answer: str
    sources: List[str]  # Список ГОСТов, использованных для ответа
    confidence: float  # Уверенность в ответе (0-1)
    query_id: Optional[str] = None
