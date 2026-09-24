from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        protected_namespaces=("settings_",),
    )

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    llm_provider: str = "deepseek"
    llm_model: str = "deepseek-flash"
    llm_base_url: str = "https://api.deepseek.com"
    llm_temperature: float = 0.0
    deepseek_api_key: SecretStr | None = None

    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    model_cache_path: Path = Path("./.cache/huggingface")
    qdrant_path: Path = Path("./data/qdrant")
    qdrant_collection: str = "agenthub_knowledge"
    rag_top_k: int = Field(default=4, ge=1, le=20)
    chunk_size: int = Field(default=500, ge=100, le=4000)
    chunk_overlap: int = Field(default=80, ge=0, le=1000)

    memory_backend: str = "redis"
    redis_url: str = "redis://localhost:6379/0"
    memory_ttl_seconds: int = Field(default=604800, ge=0)
    memory_fallback_to_local: bool = True

    mcp_server_command: str | None = None
    mcp_server_args: list[str] = Field(default_factory=list)

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized != "deepseek":
            raise ValueError("Only LLM_PROVIDER=deepseek is supported in this release.")
        return normalized

    @field_validator("memory_backend")
    @classmethod
    def validate_memory_backend(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"redis", "memory"}:
            raise ValueError("MEMORY_BACKEND must be 'redis' or 'memory'.")
        return normalized

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, value: int, info) -> int:
        chunk_size = info.data.get("chunk_size", 500)
        if value >= chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE.")
        return value

    def resolve_project_path(self, value: Path) -> Path:
        return value if value.is_absolute() else (PROJECT_ROOT / value).resolve()

    @property
    def qdrant_directory(self) -> Path:
        return self.resolve_project_path(self.qdrant_path)

    @property
    def model_cache_directory(self) -> Path:
        return self.resolve_project_path(self.model_cache_path)

    @property
    def documents_directory(self) -> Path:
        return (PROJECT_ROOT / "data" / "documents").resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

