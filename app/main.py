from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.chat import router as chat_router
from app.api.knowledge import router as knowledge_router
from app.api.schemas import HealthResponse
from app.config import get_settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgentHub",
        description=(
            "LangGraph knowledge agent with DeepSeek, dynamic tools, persistent "
            "RAG, multi-session memory, and SSE streaming."
        ),
        version=__version__,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(chat_router)
    app.include_router(knowledge_router)

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health() -> HealthResponse:
        settings = get_settings()
        return HealthResponse(
            status="ok",
            version=__version__,
            llm_provider=settings.llm_provider,
            llm_model=settings.llm_model,
            llm_key_configured=settings.deepseek_api_key is not None,
            memory_backend=settings.memory_backend,
            qdrant_path=str(settings.qdrant_directory),
            collection=settings.qdrant_collection,
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
    )

