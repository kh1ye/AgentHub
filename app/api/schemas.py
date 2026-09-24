from typing import Any

from pydantic import BaseModel, Field


SESSION_ID_PATTERN = r"^[A-Za-z0-9_-]{1,64}$"


class ChatRequest(BaseModel):
    user_id: str = Field(pattern=SESSION_ID_PATTERN)
    conversation_id: str = Field(pattern=SESSION_ID_PATTERN)
    message: str = Field(min_length=1, max_length=10000)


class SourceItem(BaseModel):
    source: str
    page: int | None = None
    score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    tool_calls: list[str] = Field(default_factory=list)
    sources: list[SourceItem] = Field(default_factory=list)


class DocumentUploadResponse(BaseModel):
    source: str
    pages: int
    chunks: int
    vector_ids: list[str]
    collection: str
    exists: bool
    points: int


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_provider: str
    llm_model: str
    llm_key_configured: bool
    memory_backend: str
    qdrant_path: str
    collection: str


class ErrorEvent(BaseModel):
    error: str
    detail: Any | None = None

