from pathlib import Path
from threading import Lock
from typing import Any

from app.config import get_settings
from app.rag.loader import load_document
from app.rag.splitter import split_documents
from app.rag.vectorstore import VectorStoreManager


class RAGService:
    def __init__(self, vectorstore: VectorStoreManager | None = None) -> None:
        self.vectorstore = vectorstore or VectorStoreManager()

    def ingest(self, path: str | Path) -> dict[str, Any]:
        source_documents = load_document(path)
        chunks = split_documents(source_documents)
        ids = self.vectorstore.add_documents(chunks)
        return {
            "source": Path(path).name,
            "pages": len(source_documents),
            "chunks": len(chunks),
            "vector_ids": ids,
            **self.vectorstore.stats(),
        }

    def search(self, query: str, *, k: int | None = None) -> list[dict[str, Any]]:
        settings = get_settings()
        matches = self.vectorstore.search(query, k=k or settings.rag_top_k)
        results = []
        for document, score in matches:
            results.append(
                {
                    "content": document.page_content,
                    "source": document.metadata.get("source", "unknown"),
                    "page": document.metadata.get("page"),
                    "chunk_index": document.metadata.get("chunk_index"),
                    "score": round(float(score), 6),
                }
            )
        return results

    def stats(self) -> dict[str, Any]:
        return self.vectorstore.stats()


_rag_service: RAGService | None = None
_rag_service_lock = Lock()


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        with _rag_service_lock:
            if _rag_service is None:
                _rag_service = RAGService()
    return _rag_service


def reset_rag_service() -> None:
    global _rag_service
    with _rag_service_lock:
        if _rag_service is not None:
            _rag_service.vectorstore.close()
        _rag_service = None

