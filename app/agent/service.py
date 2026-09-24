import asyncio
import json
from collections.abc import AsyncIterator
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from typing import Any

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from app.agent.graph import build_agent_graph
from app.llm.model import get_llm
from app.memory.factory import get_memory_backend
from app.memory.redis_memory import ConversationMemory


@dataclass
class AgentResult:
    answer: str
    tool_calls: list[str] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TokenQueueHandler(AsyncCallbackHandler):
    def __init__(self) -> None:
        self.queue: asyncio.Queue[str] = asyncio.Queue()

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        if token:
            await self.queue.put(token)


class AgentService:
    def __init__(
        self,
        *,
        memory: ConversationMemory | None = None,
        graph: Any | None = None,
    ) -> None:
        self.memory = memory or get_memory_backend()
        self._graph = graph

    @property
    def graph(self):
        if self._graph is None:
            self._graph = build_agent_graph()
        return self._graph

    def chat(self, user_id: str, conversation_id: str, message: str) -> AgentResult:
        input_messages = self._build_messages(user_id, conversation_id, message)
        state = self.graph.invoke({"messages": input_messages})
        result = self._parse_result(state["messages"])
        self.memory.append_turn(
            user_id,
            conversation_id,
            message,
            result.answer,
        )
        return result

    async def stream_chat(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
    ) -> AsyncIterator[dict[str, Any]]:
        handler = TokenQueueHandler()
        streaming_graph = build_agent_graph(
            llm=get_llm(streaming=True, callbacks=[handler])
        )
        input_messages = self._build_messages(user_id, conversation_id, message)
        task = asyncio.create_task(
            streaming_graph.ainvoke({"messages": input_messages})
        )

        while not task.done() or not handler.queue.empty():
            try:
                token = await asyncio.wait_for(handler.queue.get(), timeout=0.1)
            except TimeoutError:
                continue
            yield {"event": "token", "data": token}

        state = await task
        result = self._parse_result(state["messages"])
        self.memory.append_turn(
            user_id,
            conversation_id,
            message,
            result.answer,
        )
        yield {"event": "done", "data": result.to_dict()}

    def _build_messages(
        self,
        user_id: str,
        conversation_id: str,
        current_message: str,
    ) -> list[BaseMessage]:
        history = self.memory.load(user_id, conversation_id)
        messages: list[BaseMessage] = []
        for item in history:
            if item.get("role") == "user":
                messages.append(HumanMessage(content=item.get("content", "")))
            elif item.get("role") == "assistant":
                messages.append(AIMessage(content=item.get("content", "")))
        messages.append(HumanMessage(content=current_message))
        return messages

    @staticmethod
    def _parse_result(messages: list[BaseMessage]) -> AgentResult:
        answer = ""
        tool_calls: list[str] = []
        sources: list[dict[str, Any]] = []

        for item in messages:
            if isinstance(item, AIMessage):
                for call in item.tool_calls:
                    name = call.get("name")
                    if name and name not in tool_calls:
                        tool_calls.append(name)
                if item.content:
                    answer = _content_to_text(item.content)
            elif isinstance(item, ToolMessage):
                sources.extend(_extract_sources(item.content))

        if not answer:
            raise RuntimeError("Agent completed without a final text answer.")
        return AgentResult(
            answer=answer,
            tool_calls=tool_calls,
            sources=_deduplicate_sources(sources),
        )


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
        return "".join(parts)
    return str(content)


def _extract_sources(content: Any) -> list[dict[str, Any]]:
    if not isinstance(content, str):
        return []
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return []
    sources = payload.get("sources", []) if isinstance(payload, dict) else []
    return [item for item in sources if isinstance(item, dict)]


def _deduplicate_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for source in sources:
        key = (source.get("source"), source.get("page"))
        if key in seen:
            continue
        seen.add(key)
        result.append(source)
    return result


@lru_cache(maxsize=1)
def get_agent_service() -> AgentService:
    return AgentService()

