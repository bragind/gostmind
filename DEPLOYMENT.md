# Руководство по развертыванию GOSTMind

## Production Deployment

### Предварительные требования

1. **Инфраструктура**:
   - Сервер с Docker и Docker Compose
   - Минимум 4GB RAM, 2 CPU cores
   - 20GB свободного места на диске

2. **Внешние сервисы**:
   - Ollama сервер (локальная LLM)
   - (Опционально) Управляемые БД и Redis

### Шаги развертывания

#### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt-get update && sudo apt-get upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt-get install docker-compose-plugin -y
```

#### 2. Клонирование и настройка

```bash
# Клонирование репозитория
git clone <repository-url>
cd gostmind

# Создание .env файла
cp .env.example .env
nano .env  # Отредактируйте настройки
```

**Важно**: Измените следующие настройки в `.env`:
- `API_KEY` - используйте сильный случайный ключ
- `CORS_ORIGINS` - укажите конкретные домены вместо `*`
- `POSTGRES_PASSWORD` - используйте сильный пароль
- `LLM_BASE_URL` - URL вашего Ollama сервера (по умолчанию http://localhost:11434)
- `LLM_MODEL` - название модели Ollama (например, llama3)
- `EMBEDDING_MODEL` - модель для эмбеддингов (например, nomic-embed-text)

#### 3. Запуск сервисов

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f app
```

#### 4. Настройка Ollama (в контейнере)

Ollama уже включен в docker-compose.yml. После запуска контейнеров загрузите модели:

```bash
# Загрузка моделей в контейнер Ollama
docker-compose exec ollama ollama pull llama3
docker-compose exec ollama ollama pull nomic-embed-text

# Проверка работы
docker-compose exec ollama curl http://localhost:11434/api/tags
```

**Примечание**: Если у вас есть GPU, раскомментируйте секцию GPU в docker-compose.yml для ускорения работы.

#### 5. Индексация ГОСТов

```bash
# Поместите файлы ГОСТов в data/gosts/
# Формат: gost_XXXXX.txt

# Запуск индексации
docker-compose exec app python scripts/ingest_gosts.py
```

#### 6. Проверка работоспособности

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Тестовый запрос
curl -X POST "http://localhost:8000/api/v1/queries" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "Тестовый запрос"}'
```

### Настройка Nginx (рекомендуется)

Создайте конфигурацию Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Настройка SSL (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Мониторинг

#### Логи

```bash
# Просмотр логов приложения
docker-compose logs -f app

# Логи базы данных
docker-compose logs -f db

# Логи Redis
docker-compose logs -f cache
```

#### Резервное копирование

```bash
# Бэкап PostgreSQL
docker-compose exec db pg_dump -U user gostmind > backup_$(date +%Y%m%d).sql

# Бэкап данных ChromaDB
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz data/chroma/
```

### Обновление

```bash
# Остановка сервисов
docker-compose down

# Обновление кода
git pull

# Пересборка образа
docker-compose build

# Запуск
docker-compose up -d
```

### Масштабирование

Для production рекомендуется:

1. **Использовать управляемые сервисы**:
   - PostgreSQL: AWS RDS, Google Cloud SQL, Azure Database
   - Redis: AWS ElastiCache, Google Cloud Memorystore, Azure Cache

2. **Настроить репликацию**:
   - Master-Slave для PostgreSQL
   - Redis Sentinel для высокой доступности

3. **Использовать load balancer**:
   - Запустить несколько инстансов приложения
   - Использовать Nginx или AWS ALB для балансировки

### Безопасность

1. **Firewall**:
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

2. **Регулярные обновления**:
```bash
# Автоматические обновления безопасности
sudo apt-get install unattended-upgrades
```

3. **Мониторинг безопасности**:
   - Настройте алерты на подозрительную активность
   - Используйте fail2ban для защиты от брутфорса

### Troubleshooting

#### Приложение не запускается

```bash
# Проверка логов
docker-compose logs app

# Проверка конфигурации
docker-compose config

# Пересоздание контейнеров
docker-compose up -d --force-recreate
```

#### Проблемы с базой данных

```bash
# Проверка подключения
docker-compose exec db psql -U user -d gostmind -c "SELECT 1;"

# Проверка размера БД
docker-compose exec db psql -U user -d gostmind -c "\l+"
```

#### Проблемы с Redis

```bash
# Проверка Redis
docker-compose exec cache redis-cli ping

# Очистка кэша
docker-compose exec cache redis-cli FLUSHALL
```
