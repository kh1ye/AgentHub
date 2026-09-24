# AgentHub Demo Guide

This walkthrough demonstrates the five interview cases without opening source files
during the presentation.

## Preparation

1. Copy `.env.example` to `.env` and add `DEEPSEEK_API_KEY`.
2. Start Redis: `docker compose up -d redis`.
3. Start API: `start-agenthub.cmd`.
4. In another terminal run `scripts\ingest_demo.ps1`.
5. Keep Swagger open at <http://localhost:8000/docs>.

Use the same IDs for the memory cases:

```json
{
  "user_id": "interview_user",
  "conversation_id": "demo_001"
}
```

## Case 1: Tool Calling

Prompt:

```text
请使用工具计算 123 乘以 456。
```

Expected response metadata:

```json
{"tool_calls":["calculator"]}
```

Explain that DeepSeek receives the calculator JSON schema, emits a structured tool
call, LangGraph's ToolNode executes it, and the result returns as a ToolMessage.

## Case 2: Direct LLM

Prompt:

```text
用三句话解释 AI Agent 和普通聊天模型的区别。
```

Expected response metadata:

```json
{"tool_calls":[]}
```

Explain that `tools_condition` routes directly to END because the model did not
request a tool.

## Case 3: RAG

Prompt:

```text
请从本地知识库说明 AgentHub 的 Memory 设计，并给出来源。
```

Expected path and metadata:

```text
agent → knowledge_search → agent
tool_calls: ["knowledge_search"]
sources: [{"source":"...agenthub_demo.md", ...}]
```

Explain the ingestion path: loader, 500/80 split, local BGE, persistent Qdrant,
top-k 4, ToolMessage, final answer.

## Case 4: Multi-turn Memory

First prompt:

```text
请记住我的项目代号是 Apollo。
```

Second prompt with the same IDs:

```text
我的项目代号是什么？
```

Optional Redis inspection:

```powershell
docker compose exec redis redis-cli GET agenthub:interview_user:demo_001
```

Change `conversation_id` to `demo_002` and repeat the question to demonstrate
conversation isolation.

## Case 5: Multi-step Agent

Prompt:

```text
先查本地知识库中 AgentHub 工作流有几个逻辑阶段，再把阶段数乘以 20。
```

Expected path:

```text
agent
  → knowledge_search
  → agent
  → calculator
  → agent
  → END
```

The demo document states five stages, so the calculated result should be 100.

## SSE demonstration

Call `POST /chat/stream` from Swagger or curl. Point out separate `token` events and
the final `done` event containing `answer`, `tool_calls`, and `sources`.

## Failure demonstrations worth knowing

- Missing DeepSeek Key: chat returns a clear configuration error; `/health` still
  works.
- Redis unavailable: local development falls back to process memory when enabled.
- No Qdrant collection: `knowledge_search` reports no relevant local document.
- Unsupported upload type: API returns HTTP 415.

