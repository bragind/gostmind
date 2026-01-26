# Changelog

## [0.2.0] - 2025-01-26

### Changed
- **BREAKING**: Заменен OpenAI на локальную LLM через Ollama
- Обновлена архитектура для работы с локальными моделями
- Обновлены все зависимости

### Added
- Поддержка Ollama API для LLM и эмбеддингов
- CI/CD pipeline с автоматическими тестами и линтингом
- Документация по настройке Ollama (OLLAMA_SETUP.md)
- Интеграция Ollama в docker-compose.yml

### Removed
- Зависимость от OpenAI API
- OpenAI клиент и связанные конфигурации

### Migration Guide

Для миграции с OpenAI на Ollama:

1. Установите Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Загрузите модели:
   ```bash
   ollama pull llama3
   ollama pull nomic-embed-text
   ```

3. Обновите `.env` файл:
   ```env
   # Старые настройки (удалить)
   # OPENAI_API_KEY=...
   # OPENAI_MODEL=...
   
   # Новые настройки
   LLM_BASE_URL=http://localhost:11434
   LLM_MODEL=llama3
   EMBEDDING_BASE_URL=http://localhost:11434
   EMBEDDING_MODEL=nomic-embed-text
   ```

4. Перезапустите сервисы:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## [0.1.0] - 2025-01-26

### Added
- Начальная версия проекта
- RAG система для поиска в ГОСТах
- API endpoints для запросов и документов
- Интеграция с OpenAI
- Docker конфигурация
- Базовая документация
