from typing import Any

from langchain_openai import ChatOpenAI

from app.config import get_settings


def get_llm(**overrides: Any) -> ChatOpenAI:
    """Create the configured DeepSeek chat model.

    The API key is read only when a model client is requested, so health checks,
    imports, and offline tests do not require a secret.
    """

    settings = get_settings()
    if settings.deepseek_api_key is None:
        raise RuntimeError(
            "DEEPSEEK_API_KEY is missing. Copy .env.example to .env or set it "
            "in the current process."
        )

    options: dict[str, Any] = {
        "model": settings.llm_model,
        "api_key": settings.deepseek_api_key.get_secret_value(),
        "base_url": settings.llm_base_url,
        "temperature": settings.llm_temperature,
    }
    options.update(overrides)
    return ChatOpenAI(**options)

