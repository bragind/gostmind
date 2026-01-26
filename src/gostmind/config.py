# src/gostmind/config.py
from typing import List
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, Field, field_validator


class Settings(BaseSettings):
    # App
    app_name: str = Field(default="GOSTMind", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")

    # Security
    api_key: str = Field(..., env="API_KEY")  # для MVP — простая авторизация
    cors_origins: List[str] = Field(
        default=["*"], env="CORS_ORIGINS"
    )  # В production укажите конкретные домены

    # Database
    database_url: PostgresDsn = Field(..., env="DATABASE_URL")

    # Redis
    redis_url: RedisDsn = Field(..., env="REDIS_URL")
    redis_ttl_default: int = Field(default=3600, env="REDIS_TTL_DEFAULT")  # секунды

    # Vector Store
    chroma_path: str = Field(default="./data/chroma", env="CHROMA_PATH")
    vector_store_collection: str = Field(default="gosts", env="VECTOR_STORE_COLLECTION")

    # LLM (Ollama)
    llm_base_url: str = Field(default="http://localhost:11434", env="LLM_BASE_URL")
    llm_model: str = Field(default="llama3", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.3, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=1000, env="LLM_MAX_TOKENS")
    llm_timeout: float = Field(default=120.0, env="LLM_TIMEOUT")

    # Embeddings (Ollama)
    embedding_base_url: str = Field(default="http://localhost:11434", env="EMBEDDING_BASE_URL")
    embedding_model: str = Field(default="llama3", env="EMBEDDING_MODEL")

    # RAG Settings
    rag_top_k: int = Field(default=5, env="RAG_TOP_K")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")

    # Rate Limit
    rate_limit_requests: int = Field(default=10, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # секунды

    # Storage
    documents_path: str = Field(default="./data/gosts", env="DOCUMENTS_PATH")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
