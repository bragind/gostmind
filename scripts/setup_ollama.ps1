# PowerShell скрипт для настройки Ollama в контейнере (Windows)

$ErrorActionPreference = "Stop"

Write-Host "Setting up Ollama models..." -ForegroundColor Green

# Ждем пока Ollama будет готов
Write-Host "Waiting for Ollama to be ready..." -ForegroundColor Yellow
$timeout = 60
$elapsed = 0
$ready = $false

while (-not $ready -and $elapsed -lt $timeout) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $ready = $true
        }
    } catch {
        Write-Host "Waiting for Ollama... ($elapsed s)" -ForegroundColor Gray
        Start-Sleep -Seconds 2
        $elapsed += 2
    }
}

if (-not $ready) {
    Write-Host "Error: Ollama is not responding after $timeout seconds" -ForegroundColor Red
    exit 1
}

Write-Host "Ollama is ready!" -ForegroundColor Green

# Загружаем модели для LLM
$llmModel = if ($env:LLM_MODEL) { $env:LLM_MODEL } else { "llama3" }
Write-Host "Pulling LLM model: $llmModel" -ForegroundColor Cyan
$body = @{ name = $llmModel } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:11434/api/pull" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing

# Загружаем модели для эмбеддингов
$embeddingModel = if ($env:EMBEDDING_MODEL) { $env:EMBEDDING_MODEL } else { "nomic-embed-text" }
Write-Host "Pulling embedding model: $embeddingModel" -ForegroundColor Cyan
$body = @{ name = $embeddingModel } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:11434/api/pull" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing

Write-Host "Models setup complete!" -ForegroundColor Green
Write-Host "Available models:" -ForegroundColor Cyan
$models = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing | ConvertFrom-Json
$models.models | ForEach-Object { Write-Host "  - $($_.name)" -ForegroundColor Gray }
