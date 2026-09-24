import logging
from functools import lru_cache

from redis.exceptions import RedisError

from app.config import get_settings
from app.memory.redis_memory import ConversationMemory, InMemoryMemory, RedisMemory


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_memory_backend() -> ConversationMemory:
    settings = get_settings()
    if settings.memory_backend == "memory":
        return InMemoryMemory()

    backend = RedisMemory(
        settings.redis_url,
        ttl_seconds=settings.memory_ttl_seconds,
    )
    try:
        backend.ping()
        return backend
    except RedisError:
        if not settings.memory_fallback_to_local:
            raise
        logger.warning(
            "Redis is unavailable; using non-persistent in-memory conversation storage."
        )
        return InMemoryMemory()

