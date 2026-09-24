# 简历项目经历

## AgentHub — 基于 LangGraph 的智能知识 Agent 平台

**项目时间：2026.03–2026.09**  
**GitHub：[github.com/kh1ye/AgentHub](https://github.com/kh1ye/AgentHub)**  
**技术栈：Python / LangGraph / LangChain / FastAPI / DeepSeek / RAG / BGE / Qdrant / Redis / MCP / Docker**

- 基于 **LangGraph** 构建 `Agent → Tool → Agent` 有状态执行闭环，接入 DeepSeek Tool Calling，使模型能够按请求动态选择计算器、知识库检索和 Web Search，并在多步任务中持续消费工具结果、生成最终回答。
- 设计完整 **RAG** 链路，支持 PDF、TXT、Markdown 文档解析与递归切分，使用本地 BGE Embedding 和 Qdrant 持久化向量库完成 Top-K 检索；将检索器封装为 Agent Tool，并向接口回传文档来源与相关性分数。
- 基于 `user_id + conversation_id` 设计 **Redis 多会话记忆**，通过命名空间 Key 与 TTL 实现用户隔离、会话隔离和历史自动过期，并提供内存降级策略，保证无 Redis 环境下仍可完成本地开发与测试。
- 使用 **FastAPI** 提供对话、SSE 流式响应、文档上传及知识库统计接口，集成 MCP stdio 工具适配与 Docker Compose；编写 13 项 pytest 测试覆盖 Agent Loop、并发 RAG、Memory 隔离及 API 契约，并完成 DeepSeek、BGE/Qdrant、SSE、MCP 真实链路验证。

## 精简版（简历空间不足时使用）

**AgentHub — 基于 LangGraph 的智能知识 Agent 平台｜2026.03–2026.09**  
`Python · LangGraph · FastAPI · DeepSeek · RAG · BGE · Qdrant · Redis · MCP · Docker`  
[github.com/kh1ye/AgentHub](https://github.com/kh1ye/AgentHub)

- 构建 LangGraph 有状态 Agent Loop，支持 DeepSeek 在计算、RAG 与 Web Search 工具间动态决策，并返回工具轨迹和检索来源。
- 实现 PDF/TXT/Markdown → Chunk → BGE Embedding → Qdrant Top-K 的持久化 RAG 链路，将知识检索封装为 Agent Tool。
- 以 `user_id + conversation_id` 实现 Redis 会话隔离与 TTL，基于 FastAPI 提供异步接口和 SSE 流式响应；13 项测试覆盖 Agent、RAG、Memory 与 API。

## 60 秒面试讲解

AgentHub 是一个面向知识问答场景的有状态 Agent 后端。请求进入 FastAPI 后，系统先按用户和会话 ID 加载 Redis 历史，再交给 LangGraph 执行。DeepSeek 可以直接回答，也可以生成结构化 Tool Call；ToolNode 执行计算、RAG 或 Web Search 后，将 ToolMessage 写回状态继续推理。文档会经过解析、递归切分和本地 BGE 向量化，保存到 Qdrant，知识检索只在模型判断需要时触发。接口最终返回答案、工具轨迹和来源，同时支持 SSE 流式输出。

## 面试展示证据

- `app/agent/graph.py`：LangGraph 条件循环。
- `app/rag/`：文档加载、切分、Embedding、Qdrant 与检索模块。
- `app/memory/redis_memory.py`：会话命名空间和 TTL。
- `app/api/`：普通对话、SSE 与文档接口。
- `tests/`：13 项 Agent、RAG、Memory 和 API 测试。
