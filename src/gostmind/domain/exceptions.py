# src/gostmind/domain/exceptions.py


class GOSTMindException(Exception):
    """Базовое исключение приложения."""
    pass


class DocumentNotFoundError(GOSTMindException):
    """Документ не найден."""
    pass


class VectorStoreError(GOSTMindException):
    """Ошибка работы с векторным хранилищем."""
    pass


class LLMError(GOSTMindException):
    """Ошибка работы с LLM."""
    pass


class CacheError(GOSTMindException):
    """Ошибка работы с кэшем."""
    pass


class RateLimitExceededError(GOSTMindException):
    """Превышен лимит запросов."""
    pass
