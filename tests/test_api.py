from contextlib import contextmanager
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.agent.service import AgentResult
from app.api.chat import agent_service_dependency
from app.api.knowledge import rag_service_dependency
from app.main import app


class FakeAgentService:
    def chat(self, user_id, conversation_id, message):
        return AgentResult(
            answer=f"answer for {message}",
            tool_calls=["calculator"],
            sources=[],
        )

    async def stream_chat(self, user_id, conversation_id, message):
        yield {"event": "token", "data": "hello"}
        yield {
            "event": "done",
            "data": {"answer": "hello", "tool_calls": [], "sources": []},
        }


class FakeRAGService:
    def ingest(self, path):
        return {
            "source": path.name,
            "pages": 1,
            "chunks": 2,
            "vector_ids": ["id-1", "id-2"],
            "collection": "agenthub_knowledge",
            "exists": True,
            "points": 2,
        }

    def stats(self):
        return {"collection": "agenthub_knowledge", "exists": True, "points": 2}


@contextmanager
def overridden_client():
    app.dependency_overrides[agent_service_dependency] = lambda: FakeAgentService()
    app.dependency_overrides[rag_service_dependency] = lambda: FakeRAGService()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_health_and_chat_contracts():
    with overridden_client() as client:
        health = client.get("/health")
        chat = client.post(
            "/chat",
            json={
                "user_id": "user_001",
                "conversation_id": "conv_001",
                "message": "123 times 456",
            },
        )

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert chat.status_code == 200
    assert chat.json()["tool_calls"] == ["calculator"]


def test_sse_contract():
    with overridden_client() as client:
        response = client.post(
            "/chat/stream",
            json={
                "user_id": "user_001",
                "conversation_id": "conv_001",
                "message": "hello",
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: token" in response.text
    assert "event: done" in response.text


def test_document_upload_contract(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.api.knowledge.get_settings",
        lambda: SimpleNamespace(documents_directory=tmp_path),
    )
    with overridden_client() as client:
        response = client.post(
            "/documents/upload",
            files={"file": ("guide.md", b"# AgentHub\nLangGraph guide", "text/markdown")},
        )

    assert response.status_code == 200
    assert response.json()["chunks"] == 2

