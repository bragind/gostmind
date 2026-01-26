# Ollama в Docker контейнере

## Быстрый старт

Ollama уже настроен в `docker-compose.yml` и запускается автоматически вместе с другими сервисами.

### 1. Запуск

```bash
docker-compose up -d
```

Это запустит все сервисы, включая Ollama.

### 2. Загрузка моделей

После запуска контейнеров загрузите необходимые модели:

```bash
# LLM модель для генерации ответов
docker-compose exec ollama ollama pull llama3

# Модель для эмбеддингов
docker-compose exec ollama ollama pull nomic-embed-text
```

### 3. Проверка работы

```bash
# Проверка доступности
curl http://localhost:11434/api/tags

# Тест генерации
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Привет!"
}'
```

## Конфигурация

### Переменные окружения

В `.env` файле настройте:

```env
LLM_BASE_URL=http://ollama:11434  # Внутри Docker сети
# или
LLM_BASE_URL=http://localhost:11434  # С хоста

LLM_MODEL=llama3
EMBEDDING_BASE_URL=http://ollama:11434
EMBEDDING_MODEL=nomic-embed-text
```

**Важно**: 
- Внутри Docker сети используйте `http://ollama:11434`
- С хоста используйте `http://localhost:11434`

### Использование GPU

Если у вас есть NVIDIA GPU, раскомментируйте секцию в `docker-compose.yml`:

```yaml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Также убедитесь, что установлен `nvidia-container-toolkit`:

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Ограничения ресурсов

Вы можете ограничить использование ресурсов Ollama, создав `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  ollama:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 16G
        reservations:
          cpus: '2'
          memory: 8G
```

## Управление моделями

### Список моделей

```bash
docker-compose exec ollama ollama list
```

### Удаление модели

```bash
docker-compose exec ollama ollama rm <model-name>
```

### Просмотр информации о модели

```bash
docker-compose exec ollama ollama show <model-name>
```

## Персистентное хранение

Модели и данные Ollama хранятся в Docker volume `ollama_data`. Это означает, что данные сохраняются между перезапусками контейнеров.

### Резервное копирование

```bash
# Создание бэкапа
docker run --rm -v gostmind_ollama_data:/data -v $(pwd):/backup alpine tar czf /backup/ollama_backup.tar.gz /data

# Восстановление
docker run --rm -v gostmind_ollama_data:/data -v $(pwd):/backup alpine tar xzf /backup/ollama_backup.tar.gz -C /
```

## Troubleshooting

### Контейнер не запускается

```bash
# Проверка логов
docker-compose logs ollama

# Проверка статуса
docker-compose ps ollama
```

### Модели не загружаются

1. Проверьте доступное место на диске:
   ```bash
   docker system df
   ```

2. Проверьте логи:
   ```bash
   docker-compose logs ollama
   ```

3. Попробуйте загрузить модель вручную:
   ```bash
   docker-compose exec ollama ollama pull llama3
   ```

### Медленная работа

1. **Используйте GPU** (см. раздел выше)
2. **Используйте более легкие модели**:
   - Для LLM: `llama3:8b` вместо `llama3:70b`
   - Для эмбеддингов: `all-minilm` вместо `nomic-embed-text`
3. **Увеличьте ресурсы** контейнера

### Проблемы с памятью

Для больших моделей требуется много RAM:
- `llama3` (8B): ~8GB RAM
- `llama3:70b`: ~40GB RAM

Используйте квантованные версии для экономии памяти:
```bash
docker-compose exec ollama ollama pull llama3:8b-q4_0
```

## Обновление Ollama

```bash
# Остановка контейнера
docker-compose stop ollama

# Обновление образа
docker-compose pull ollama

# Запуск с новым образом
docker-compose up -d ollama
```

## Мониторинг

### Использование ресурсов

```bash
docker stats gostmind_ollama
```

### Логи в реальном времени

```bash
docker-compose logs -f ollama
```

### Проверка здоровья

```bash
curl http://localhost:11434/api/tags
```
