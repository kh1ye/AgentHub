from collections.abc import Sequence

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import BaseTool

from app.agent.state import AgentState


SYSTEM_PROMPT = """You are AgentHub, a precise AI knowledge assistant.

Rules:
1. Use calculator for arithmetic instead of calculating mentally.
2. Use knowledge_search when the user asks about uploaded or local documents.
3. Use web_search only when current public information is needed and the local
   knowledge base is insufficient.
4. You may call multiple tools in sequence to complete a multi-step request.
5. Ground document answers in tool output and mention source filenames.
6. If evidence is missing, say so clearly instead of inventing an answer.
7. Reply in the user's language and keep the final answer concise.
"""


def create_agent_node(
    model: BaseChatModel,
    tools: Sequence[BaseTool],
) -> RunnableLambda:
    model_with_tools = model.bind_tools(list(tools))

    def call_model(state: AgentState) -> dict[str, list]:
        response = model_with_tools.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        )
        return {"messages": [response]}

    async def call_model_async(state: AgentState) -> dict[str, list]:
        response = await model_with_tools.ainvoke(
            [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        )
        return {"messages": [response]}

    return RunnableLambda(call_model, afunc=call_model_async, name="agent")

