#!/bin/bash
# Скрипт для настройки Ollama в контейнере

set -e

echo "Setting up Ollama models..."

# Проверяем наличие curl или wget
if command -v curl &> /dev/null; then
    HTTP_CLIENT="curl"
    HTTP_FLAGS="-f -s"
    HTTP_POST_FLAGS="-X POST -H Content-Type:application/json -d"
elif command -v wget &> /dev/null; then
    HTTP_CLIENT="wget"
    HTTP_FLAGS="-q -O -"
    HTTP_POST_FLAGS="--post-data"
else
    echo "Error: Neither curl nor wget found. Please install one of them."
    exit 1
fi

# Ждем пока Ollama будет готов
echo "Waiting for Ollama to be ready..."
timeout=120
elapsed=0
while true; do
    if [ "$HTTP_CLIENT" = "curl" ]; then
        if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
            break
        fi
    else
        if wget -q -O - http://localhost:11434/api/tags > /dev/null 2>&1; then
            break
        fi
    fi
    
    if [ $elapsed -ge $timeout ]; then
        echo "Error: Ollama is not responding after ${timeout} seconds"
        exit 1
    fi
    echo "Waiting for Ollama... (${elapsed}s)"
    sleep 2
    elapsed=$((elapsed + 2))
done

echo "Ollama is ready!"

# Загружаем модели для LLM
LLM_MODEL=${LLM_MODEL:-llama3}
echo "Pulling LLM model: ${LLM_MODEL}"

if [ "$HTTP_CLIENT" = "curl" ]; then
    curl -X POST http://localhost:11434/api/pull -H "Content-Type: application/json" -d "{\"name\": \"${LLM_MODEL}\"}"
else
    echo "{\"name\": \"${LLM_MODEL}\"}" | wget --post-data=- --header="Content-Type: application/json" -O - http://localhost:11434/api/pull
fi

# Загружаем модели для эмбеддингов
EMBEDDING_MODEL=${EMBEDDING_MODEL:-nomic-embed-text}
echo "Pulling embedding model: ${EMBEDDING_MODEL}"

if [ "$HTTP_CLIENT" = "curl" ]; then
    curl -X POST http://localhost:11434/api/pull -H "Content-Type: application/json" -d "{\"name\": \"${EMBEDDING_MODEL}\"}"
else
    echo "{\"name\": \"${EMBEDDING_MODEL}\"}" | wget --post-data=- --header="Content-Type: application/json" -O - http://localhost:11434/api/pull
fi

echo "Models setup complete!"
echo "Available models:"
if [ "$HTTP_CLIENT" = "curl" ]; then
    curl -s http://localhost:11434/api/tags | python3 -m json.tool 2>/dev/null || curl -s http://localhost:11434/api/tags
else
    wget -q -O - http://localhost:11434/api/tags | python3 -m json.tool 2>/dev/null || wget -q -O - http://localhost:11434/api/tags
fi
