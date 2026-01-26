# src/gostmind/domain/models/standard.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Standard:
    """Доменная модель ГОСТ."""
    number: str  # Номер ГОСТ, например "ГОСТ 16093"
    title: str
    content: str
    file_path: Optional[str] = None
    indexed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.indexed_at is None:
            self.indexed_at = datetime.utcnow()
