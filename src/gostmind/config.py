# src/gostmind/config.py
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, Field


class Settings(BaseSettings):
    # App
    app_name: str = "GOSTMind"
    debug: bool = Field(default=False, env="DEBUG")

    # Security
    api_key: str = Field(..., env="API_KEY")  # для MVP — простая авторизация

    # Database
    database_url: PostgresDsn = Field(..., env="DATABASE_URL")

    # Redis
    redis_url: RedisDsn = Field(..., env="REDIS_URL")

    # Vector Store
    chroma_path: str = Field(default="./data/chroma", env="CHROMA_PATH")

    # LLM
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")

    # Rate Limit
    rate_limit_requests: int = Field(default=10, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # секунды

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()