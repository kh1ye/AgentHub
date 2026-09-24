import os

import pytest

from app.agent.service import get_agent_service
from app.config import get_settings
from app.memory.factory import get_memory_backend
from app.rag.embeddings import get_embeddings
from app.rag.retriever import reset_rag_service


@pytest.fixture(autouse=True)
def clear_singletons():
    os.environ.setdefault("MEMORY_BACKEND", "memory")
    get_settings.cache_clear()
    get_memory_backend.cache_clear()
    get_agent_service.cache_clear()
    reset_rag_service()
    get_embeddings.cache_clear()
    yield
    get_settings.cache_clear()
    get_memory_backend.cache_clear()
    get_agent_service.cache_clear()
    reset_rag_service()
    get_embeddings.cache_clear()

