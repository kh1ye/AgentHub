import json

import pytest
from langchain_core.messages import AIMessage, ToolMessage

from app.agent.graph import build_agent_graph
from app.agent.service import AgentService
from app.memory.redis_memory import InMemoryMemory
from app.tools.calculator import calculator


class ToolCallingFakeModel:
    def bind_tools(self, tools):
        self.tools = tools
        return self

    def invoke(self, messages):
        if any(isinstance(message, ToolMessage) for message in messages):
            return AIMessage(content="123 × 456 = 56088")
        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "calculator",
                    "args": {"a": 123, "b": 456, "operation": "multiply"},
                    "id": "call_calculator_1",
                    "type": "tool_call",
                }
            ],
        )

    async def ainvoke(self, messages):
        return self.invoke(messages)


def test_langgraph_executes_tool_loop():
    graph = build_agent_graph(llm=ToolCallingFakeModel(), tools=[calculator])

    state = graph.invoke({"messages": [("user", "计算 123 乘以 456")]})

    assert state["messages"][-1].content == "123 × 456 = 56088"
    assert any(isinstance(message, ToolMessage) for message in state["messages"])
    tool_message = next(
        message for message in state["messages"] if isinstance(message, ToolMessage)
    )
    assert float(tool_message.content) == 56088


class RecordingGraph:
    def __init__(self):
        self.calls = []

    def invoke(self, state):
        self.calls.append(state["messages"])
        return {
            "messages": [
                *state["messages"],
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "knowledge_search",
                            "args": {"query": "LangGraph"},
                            "id": "call_rag_1",
                            "type": "tool_call",
                        }
                    ],
                ),
                ToolMessage(
                    content=json.dumps(
                        {
                            "sources": [
                                {"source": "guide.md", "page": None, "score": 0.9}
                            ]
                        }
                    ),
                    tool_call_id="call_rag_1",
                ),
                AIMessage(content="LangGraph is a stateful agent workflow framework."),
            ]
        }


def test_agent_service_saves_turn_and_extracts_metadata():
    memory = InMemoryMemory()
    graph = RecordingGraph()
    service = AgentService(memory=memory, graph=graph)

    result = service.chat("user_001", "conv_001", "What is LangGraph?")

    assert result.tool_calls == ["knowledge_search"]
    assert result.sources[0]["source"] == "guide.md"
    assert memory.load("user_001", "conv_001") == [
        {"role": "user", "content": "What is LangGraph?"},
        {
            "role": "assistant",
            "content": "LangGraph is a stateful agent workflow framework.",
        },
    ]

    service.chat("user_001", "conv_001", "What did I ask?")
    assert len(graph.calls[1]) == 3


def test_calculator_rejects_division_by_zero():
    with pytest.raises(ValueError, match="Division by zero"):
        calculator.invoke({"a": 1, "b": 0, "operation": "divide"})

