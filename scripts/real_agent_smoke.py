import asyncio
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.service import AgentService
from app.memory.redis_memory import InMemoryMemory


async def stream_check(service: AgentService) -> dict:
    events = []
    async for event in service.stream_chat(
        "smoke_user",
        "stream_conversation",
        "只回复 STREAM_OK，不要调用工具。",
    ):
        events.append(event)
    tokens = [event["data"] for event in events if event["event"] == "token"]
    done = next(event["data"] for event in events if event["event"] == "done")
    return {
        "token_count": len(tokens),
        "streamed_text": "".join(tokens),
        "done": done,
    }


def main() -> None:
    service = AgentService(memory=InMemoryMemory())
    calculator_result = service.chat(
        "smoke_user",
        "calculator_conversation",
        "必须使用 calculator 工具计算 123 乘以 456，并只给出最终结果。",
    )
    rag_result = service.chat(
        "smoke_user",
        "rag_conversation",
        "必须使用 knowledge_search 工具，从本地知识库说明 AgentHub 如何隔离不同会话，并给出来源。",
    )
    stream_result = asyncio.run(stream_check(service))
    print(
        json.dumps(
            {
                "status": "ok",
                "calculator": calculator_result.to_dict(),
                "rag": rag_result.to_dict(),
                "stream": stream_result,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
