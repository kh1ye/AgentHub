import hashlib
import math
import re
from concurrent.futures import ThreadPoolExecutor

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.rag.vectorstore import VectorStoreManager
from app.rag.retriever import get_rag_service, reset_rag_service


class HashEmbeddings(Embeddings):
    dimensions = 32

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", text.lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            vector[digest[0] % self.dimensions] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def test_qdrant_persists_and_reopens(tmp_path):
    documents = [
        Document(
            page_content="LangGraph manages stateful agent workflows and tool loops.",
            metadata={"source": "langgraph.md", "chunk_index": 0},
        ),
        Document(
            page_content="Redis stores session memory with durable keys.",
            metadata={"source": "redis.md", "chunk_index": 0},
        ),
    ]
    manager = VectorStoreManager(
        path=tmp_path / "qdrant",
        collection_name="test_knowledge",
        embeddings=HashEmbeddings(),
    )
    manager.add_documents(documents)
    assert manager.stats()["points"] == 2
    manager.close()

    reopened = VectorStoreManager(
        path=tmp_path / "qdrant",
        collection_name="test_knowledge",
        embeddings=HashEmbeddings(),
    )
    matches = reopened.search("LangGraph agent workflow", k=1)

    assert matches[0][0].metadata["source"] == "langgraph.md"
    reopened.close()


def test_rag_singleton_is_thread_safe():
    reset_rag_service()
    with ThreadPoolExecutor(max_workers=8) as executor:
        services = list(executor.map(lambda _: get_rag_service(), range(32)))

    assert len({id(service) for service in services}) == 1
    reset_rag_service()

