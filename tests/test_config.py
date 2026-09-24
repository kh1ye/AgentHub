from unittest.mock import patch

import pytest

from app.config import get_settings
from app.llm.model import get_llm


def test_deepseek_settings_and_secret_redaction(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret-test-value")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.llm_provider == "deepseek"
    assert settings.llm_model == "deepseek-flash"
    assert "secret-test-value" not in repr(settings)


def test_get_llm_uses_centralized_configuration(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret-test-value")
    get_settings.cache_clear()

    with patch("app.llm.model.ChatOpenAI") as chat_openai:
        get_llm(streaming=True)

    kwargs = chat_openai.call_args.kwargs
    assert kwargs["model"] == "deepseek-flash"
    assert kwargs["base_url"] == "https://api.deepseek.com"
    assert kwargs["api_key"] == "secret-test-value"
    assert kwargs["streaming"] is True


def test_get_llm_fails_clearly_without_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        get_llm()

