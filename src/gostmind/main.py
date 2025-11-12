# src/gostmind/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.v1.routes import queries, health
from .deps import verify_api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: можно инициализировать Chroma, кэш и т.п.
    yield
    # Shutdown: очистка ресурсов


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AI-ассистент для конструкторов: справочник по ГОСТ",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS (настройте по необходимости)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(
        health.router,
        prefix="/api/v1",
        tags=["Health"]
    )
    app.include_router(
        queries.router,
        prefix="/api/v1",
        tags=["Queries"],
        dependencies=[Depends(verify_api_key)]
    )

    return app


app = create_app()