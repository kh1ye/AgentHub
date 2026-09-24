from pathlib import Path
from threading import RLock
from typing import Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models

from app.config import get_settings
from app.rag.embeddings import get_embeddings


class VectorStoreManager:
    def __init__(
        self,
        *,
        path: str | Path | None = None,
        collection_name: str | None = None,
        embeddings: Embeddings | None = None,
    ) -> None:
        settings = get_settings()
        self.path = Path(path or settings.qdrant_directory).resolve()
        self.collection_name = collection_name or settings.qdrant_collection
        self._embeddings = embeddings
        self._client: QdrantClient | None = None
        self._store: QdrantVectorStore | None = None
        self._lock = RLock()

    @property
    def embeddings(self) -> Embeddings:
        if self._embeddings is None:
            self._embeddings = get_embeddings()
        return self._embeddings

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            with self._lock:
                if self._client is None:
                    self.path.mkdir(parents=True, exist_ok=True)
                    self._client = QdrantClient(path=str(self.path))
        return self._client

    def collection_exists(self) -> bool:
        return self.client.collection_exists(self.collection_name)

    def get_store(self, *, create: bool = False) -> QdrantVectorStore:
        if self._store is not None:
            return self._store
        with self._lock:
            if self._store is not None:
                return self._store
            if not self.collection_exists():
                if not create:
                    raise LookupError(
                        "Knowledge collection does not exist. Upload a document first."
                    )
                vector_size = len(self.embeddings.embed_query("dimension probe"))
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                    ),
                )

            self._store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings,
            )
        return self._store

    def add_documents(self, documents: list[Document]) -> list[str]:
        if not documents:
            return []
        return self.get_store(create=True).add_documents(documents)

    def search(self, query: str, *, k: int) -> list[tuple[Document, float]]:
        if not self.collection_exists():
            return []
        return self.get_store().similarity_search_with_score(query, k=k)

    def stats(self) -> dict[str, Any]:
        if not self.collection_exists():
            return {
                "collection": self.collection_name,
                "exists": False,
                "points": 0,
            }
        count = self.client.count(
            collection_name=self.collection_name,
            exact=True,
        ).count
        return {
            "collection": self.collection_name,
            "exists": True,
            "points": count,
        }

    def close(self) -> None:
        with self._lock:
            if self._client is not None:
                self._client.close()
            self._client = None
            self._store = None

