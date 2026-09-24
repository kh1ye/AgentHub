from collections.abc import Sequence

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.nodes import create_agent_node
from app.agent.state import AgentState
from app.llm.model import get_llm
from app.tools import calculator, knowledge_search, web_search


def build_agent_graph(
    *,
    llm: BaseChatModel | None = None,
    tools: Sequence[BaseTool] | None = None,
):
    selected_tools = list(tools or [calculator, knowledge_search, web_search])
    selected_llm = llm or get_llm()

    builder = StateGraph(AgentState)
    builder.add_node("agent", create_agent_node(selected_llm, selected_tools))
    builder.add_node(
        "tools",
        ToolNode(selected_tools, handle_tool_errors=True),
    )
    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", END: END},
    )
    builder.add_edge("tools", "agent")
    return builder.compile()

