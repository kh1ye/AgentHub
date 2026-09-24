# Resume Project Entry

## AgentHub — 基于 LangGraph 的智能知识 Agent 平台

**2026.03–2026.09**  
**Python / FastAPI / LangGraph / LangChain / DeepSeek / RAG / BGE / Qdrant / Redis / MCP / Docker**

- 基于 LangGraph 构建具备状态管理与循环工具调用能力的智能 Agent，通过 DeepSeek
  Tool Calling 动态选择知识检索、计算及 Web Search，并返回可观测的工具调用轨迹。
- 设计 PDF/TXT/Markdown 知识入库链路，实现递归文本切分、本地 BGE Embedding、
  Qdrant 持久化向量检索与 Top-K source 回传，将 RAG 封装为按需调用的 Agent Tool。
- 基于 `user_id + conversation_id` 设计 Redis 多会话 Memory，使用
  `agenthub:{user_id}:{conversation_id}` 实现用户与会话隔离，并通过 TTL 管理历史数据。
- 使用 FastAPI 提供 Agent、文档上传、健康检查及 SSE 流式接口，配套 Docker Compose、
  MCP stdio 示例、Swagger 文档与 12 项离线测试，覆盖 Agent Loop、RAG 持久化和 API 契约。

## 60-second explanation

这个项目的核心不是聊天接口，而是一条可观察的 Agent 执行链。用户请求进入 FastAPI
后，服务先根据用户和会话 ID 从 Redis 加载历史，再把消息交给 LangGraph。DeepSeek
可以直接回答，也可以生成结构化 Tool Call；ToolNode 执行计算、RAG 或 Web Search，
结果作为 ToolMessage 写回状态并继续循环。文档通过本地 BGE 向量化并持久化到 Qdrant，
所以 RAG 只在模型判断需要时触发。最终接口同时返回回答、工具名和来源，并支持 SSE。

## Evidence you can show

- `app/agent/graph.py`: explicit conditional LangGraph loop.
- `app/rag/`: loader, splitter, embedding, Qdrant, retriever modules.
- `app/memory/redis_memory.py`: session key and TTL implementation.
- `tests/test_agent.py`: real ToolNode loop without paid API calls.
- `tests/test_rag.py`: Qdrant close/reopen persistence test.

