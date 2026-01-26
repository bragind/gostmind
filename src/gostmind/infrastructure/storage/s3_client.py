# src/gostmind/infrastructure/storage/s3_client.py
# Заглушка для будущей интеграции с S3
# В production можно использовать boto3 или aioboto3
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class S3Client:
    """Класс для работы с S3 (заглушка для будущей реализации)."""
    
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        logger.info("S3Client initialized (stub)", bucket=bucket_name)
    
    async def upload_file(self, local_path: str, s3_key: str) -> bool:
        """Загрузить файл в S3."""
        logger.warning("S3Client.upload_file not implemented")
        return False
    
    async def download_file(self, s3_key: str, local_path: str) -> bool:
        """Скачать файл из S3."""
        logger.warning("S3Client.download_file not implemented")
        return False
    
    async def list_files(self, prefix: str = "") -> list:
        """Получить список файлов в S3."""
        logger.warning("S3Client.list_files not implemented")
        return []
