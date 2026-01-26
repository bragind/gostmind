# Настройка Ollama для GOSTMind

## Установка Ollama

### Рекомендуемый способ: через Docker Compose

Ollama уже настроен в `docker-compose.yml`. Просто запустите:

```bash
docker-compose up -d ollama
```

### Альтернативные способы

#### На сервере Linux (без Docker)

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### На Windows

Скачайте установщик с [ollama.com](https://ollama.com/download)

#### Через Docker (вручную)

```bash
docker pull ollama/ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

## Загрузка моделей

### Для LLM (генерация ответов)

Рекомендуемые модели:
- **llama3** (8B) - хороший баланс качества и скорости
- **llama3:70b** - лучшее качество, требует больше ресурсов
- **mistral** - альтернатива, быстрая
- **qwen2** - хорошая поддержка русского языка

```bash
# Если Ollama в контейнере Docker:
docker-compose exec ollama ollama pull llama3

# Или для лучшего качества
docker-compose exec ollama ollama pull llama3:70b

# Если Ollama установлен локально:
ollama pull llama3
ollama pull llama3:70b
```

### Для эмбеддингов

Для эмбеддингов можно использовать:
- **llama3** (если поддерживает embeddings)
- **nomic-embed-text** - специализированная модель для эмбеддингов
- **all-minilm** - легкая модель для эмбеддингов

```bash
# Если Ollama в контейнере Docker:
docker-compose exec ollama ollama pull nomic-embed-text

# Если Ollama установлен локально:
ollama pull nomic-embed-text
```

## Проверка работы

```bash
# Если Ollama в контейнере:
docker-compose exec ollama curl http://localhost:11434/api/tags

# Или с хоста (если порт проброшен):
curl http://localhost:11434/api/tags

# Тест генерации
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Привет, как дела?"
}'

# Тест эмбеддингов
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "Тестовый текст"
}'
```

## Настройка для production

### 1. Переменные окружения

В `.env` файле укажите:

```env
LLM_BASE_URL=http://your-ollama-server:11434
LLM_MODEL=llama3
EMBEDDING_BASE_URL=http://your-ollama-server:11434
EMBEDDING_MODEL=nomic-embed-text
```

### 2. Оптимизация производительности

Для лучшей производительности рекомендуется:

1. **Использовать GPU** (если доступно):
   ```bash
   # Установка CUDA для Ollama
   # Следуйте инструкциям на ollama.com
   ```

2. **Настроить количество воркеров**:
   - Для LLM: обычно 1-2 воркера достаточно
   - Для эмбеддингов: можно больше воркеров для параллельной обработки

3. **Использовать более легкие модели** для эмбеддингов:
   - `all-minilm` - быстрая и легкая
   - `nomic-embed-text` - хороший баланс

### 3. Мониторинг

```bash
# Проверка использования ресурсов
docker-compose stats ollama
# или
docker stats gostmind_ollama

# Просмотр логов
docker-compose logs -f ollama
# или
docker logs -f gostmind_ollama
```

## Troubleshooting

### Модель не загружается

```bash
# Проверка доступного места
docker system df

# Очистка неиспользуемых моделей (в контейнере)
docker-compose exec ollama ollama list
docker-compose exec ollama ollama rm <model-name>

# Если Ollama установлен локально:
ollama list
ollama rm <model-name>
```

### Медленная работа

1. Проверьте использование GPU:
   ```bash
   nvidia-smi
   ```

2. Используйте более легкие модели
3. Увеличьте таймауты в конфигурации

### Проблемы с памятью

Для больших моделей требуется много RAM:
- llama3 (8B): ~8GB RAM
- llama3:70b: ~40GB RAM

Рассмотрите использование квантованных версий (q4, q5).
