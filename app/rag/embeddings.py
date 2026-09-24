import os
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.config import get_settings


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    settings = get_settings()
    cache_directory = settings.model_cache_directory
    cache_directory.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(cache_directory))
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(cache_directory))
    os.environ.setdefault("TORCH_HOME", str(cache_directory / "torch"))
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        cache_folder=str(cache_directory),
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

