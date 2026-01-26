FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml ./

# Установка зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Копирование исходного кода
COPY src/ ./src/
COPY scripts/ ./scripts/

# Создание директорий для данных
RUN mkdir -p /app/data/chroma /app/data/gosts

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Порт приложения
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/api/v1/health', timeout=5)"

# Запуск приложения
CMD ["uvicorn", "gostmind.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
