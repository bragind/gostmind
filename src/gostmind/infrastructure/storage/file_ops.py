# src/gostmind/infrastructure/storage/file_ops.py
from pathlib import Path
from typing import List, Optional
import structlog

logger = structlog.get_logger(__name__)


class FileStorage:
    """Класс для работы с файловой системой."""

    def __init__(self, base_path: str = "./data/gosts"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def list_files(self, extension: str = ".txt") -> List[Path]:
        """Получить список файлов с указанным расширением."""
        return list(self.base_path.glob(f"*{extension}"))

    def read_file(self, file_path: str) -> Optional[str]:
        """Прочитать содержимое файла."""
        path = self.base_path / file_path
        if not path.exists():
            logger.warning("File not found", path=str(path))
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error("Failed to read file", path=str(path), error=str(e))
            return None

    def file_exists(self, file_path: str) -> bool:
        """Проверить существование файла."""
        path = self.base_path / file_path
        return path.exists()
