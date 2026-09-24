import json

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from app.agent.service import AgentService, get_agent_service
from app.api.schemas import ChatRequest, ChatResponse


router = APIRouter(tags=["chat"])


def agent_service_dependency() -> AgentService:
    return get_agent_service()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: AgentService = Depends(agent_service_dependency),
) -> ChatResponse:
    result = await run_in_threadpool(
        service.chat,
        request.user_id,
        request.conversation_id,
        request.message,
    )
    return ChatResponse(**result.to_dict())


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    service: AgentService = Depends(agent_service_dependency),
) -> StreamingResponse:
    async def event_stream():
        try:
            async for event in service.stream_chat(
                request.user_id,
                request.conversation_id,
                request.message,
            ):
                data = json.dumps(event["data"], ensure_ascii=False)
                yield f"event: {event['event']}\ndata: {data}\n\n"
        except Exception as exc:
            data = json.dumps({"error": str(exc)}, ensure_ascii=False)
            yield f"event: error\ndata: {data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

