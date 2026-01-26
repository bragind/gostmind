# GOSTMind

Интеллектуальный помощник инженера для упрощения поиска информации в ГОСТах на основе RAG (Retrieval-Augmented Generation).

## 📋 Описание

GOSTMind - это AI-ассистент, который помогает инженерам быстро находить нужную информацию в ГОСТах. Система использует:
- **RAG (Retrieval-Augmented Generation)** для поиска релевантных фрагментов ГОСТов
- **Векторное хранилище (ChromaDB)** для эффективного поиска
- **Локальная LLM (Ollama)** для генерации ответов на основе найденных документов
- **Redis** для кэширования запросов и rate limiting

## 🏗 Архитектура

Проект следует принципам Clean Architecture:

```
src/gostmind/
├── api/              # API слой (FastAPI routes, schemas)
├── application/      # Use cases (бизнес-логика)
├── domain/           # Доменные модели и исключения
└── infrastructure/   # Внешние зависимости (DB, LLM, Vector Store)
```

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- Docker и Docker Compose
- OpenAI API ключ

### Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd gostmind
```

2. Создайте файл `.env`:
```bash
cp .env.example .env
# Отредактируйте .env и укажите ваши настройки
```

3. Запустите через Docker Compose:
```bash
docker-compose up -d
```

4. Настройте модели Ollama (опционально, если нужно загрузить модели):
```bash
# Модели можно загрузить вручную после запуска контейнера
docker-compose exec ollama ollama pull llama3
docker-compose exec ollama ollama pull nomic-embed-text

# Или использовать скрипт
docker-compose exec ollama bash /app/scripts/setup_ollama.sh
```

5. Индексируйте ГОСТы:
```bash
# Поместите файлы ГОСТов в data/gosts/
docker-compose exec app python scripts/ingest_gosts.py
```

### Локальная разработка

1. Установите зависимости:
```bash
pip install -e ".[dev]"
```

2. Запустите сервисы (PostgreSQL, Redis, Ollama):
```bash
docker-compose up -d db cache ollama
```

3. Настройте модели Ollama (если еще не настроены):
```bash
# В контейнере Ollama
docker-compose exec ollama ollama pull llama3
docker-compose exec ollama ollama pull nomic-embed-text
```

4. Запустите приложение:
```bash
uvicorn gostmind.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Документация

После запуска приложения доступна интерактивная документация:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Основные endpoints

- `GET /api/v1/health` - Проверка здоровья сервиса
- `POST /api/v1/queries` - Обработка запроса пользователя
- `POST /api/v1/documents/upload` - Загрузка и индексация документа
- `GET /api/v1/documents` - Список проиндексированных документов

### Пример запроса

```bash
curl -X POST "http://localhost:8000/api/v1/queries" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Какие требования к маркировке продукции?",
    "user_id": "user123"
  }'
```

## ⚙️ Конфигурация

Основные настройки в файле `.env`:

```env
# Безопасность
API_KEY=your-secret-api-key

# База данных
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/gostmind

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM (Ollama)
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3

# Embeddings (Ollama)
EMBEDDING_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text

# Векторное хранилище
CHROMA_PATH=./data/chroma

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60
```

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# С линтером
ruff check src/
mypy src/
```

## 📦 Production Deployment

### Рекомендации для production:

1. **Безопасность**:
   - Измените `CORS_ORIGINS` на конкретные домены
   - Используйте сильный `API_KEY`
   - Рассмотрите использование JWT токенов вместо простого API ключа

2. **Масштабирование**:
   - Используйте внешний PostgreSQL (RDS, Cloud SQL)
   - Используйте управляемый Redis (ElastiCache, Cloud Memorystore)
   - Рассмотрите использование S3 для хранения документов

3. **Мониторинг**:
   - Добавьте Prometheus метрики
   - Настройте логирование в централизованную систему (ELK, Loki)
   - Настройте алерты

4. **Производительность**:
   - Настройте connection pooling для БД
   - Используйте CDN для статических файлов
   - Используйте более мощные модели Ollama для production (llama3:70b, mistral:large)
   - Настройте GPU для ускорения работы LLM

## 🔧 Улучшения для production

### Планируемые улучшения:

- [ ] Аутентификация через JWT
- [ ] Интеграция с S3 для хранения документов
- [ ] Метрики Prometheus
- [ ] Расширенное логирование и трейсинг
- [ ] Поддержка множественных коллекций
- [ ] Веб-интерфейс для управления
- [ ] Поддержка PDF и других форматов
- [ ] Автоматическое обновление индекса

## 📝 Лицензия

[Укажите лицензию]

## 👥 Авторы

[Укажите авторов]
