# 简历项目经历

## 正式简历版

### AgentHub — 基于 LangGraph 的智能知识 Agent 平台　　2026.3–2026.9

**GitHub：** [https://github.com/kh1ye/AgentHub](https://github.com/kh1ye/AgentHub)

**项目简介：** 面向企业知识问答与多轮任务场景，针对大模型无法直接访问私有文档、工具调用缺少执行闭环以及多用户会话状态难隔离等问题，设计并实现具备知识检索、工具调用、会话记忆与流式响应能力的智能 Agent 后端；打通“用户请求 → Agent 决策 → 工具执行 → 结果回传 → 继续推理”的完整链路。

**技术栈：** Python / LangGraph / LangChain / FastAPI / DeepSeek / RAG / BGE / Qdrant / Redis / MCP / Docker

**项目内容：**

1. **Agent Runtime 与工具编排：** 基于 LangGraph StateGraph 构建 `Agent → Tool → Agent` 条件循环，通过 DeepSeek Tool Calling 在直接回答、计算器、知识库检索与 Web Search 间动态路由；将工具执行结果以 ToolMessage 写回状态继续推理，并向接口返回工具调用轨迹与引用来源。
2. **RAG 知识库链路：** 实现 PDF、TXT、Markdown 文档加载、递归文本切分、本地 BGE Embedding、Qdrant 持久化存储与 Top-K 检索；将 Retriever 封装为 Agent Tool，支持文档来源和相关性分数回传，并通过单例及初始化锁解决并发检索时的本地 Qdrant 资源竞争问题。
3. **多用户会话记忆：** 基于 Redis 设计 `agenthub:{user_id}:{conversation_id}` 会话命名空间，通过用户 ID 与会话 ID 实现数据隔离，结合 TTL 管理历史自动过期；提供 In-Memory 降级后端，使无 Redis 环境仍可完成本地开发与接口测试。
4. **异步服务与流式输出：** 使用 FastAPI 封装普通对话、SSE 流式响应、文档上传、知识库统计与健康检查接口；通过异步回调实时推送模型 Token，并集成 MCP stdio 客户端，实现外部工具发现与统一调用。
5. **工程化与质量验证：** 抽离统一 LLM 配置层，通过环境变量切换模型和服务参数，使用 Docker Compose 编排 API 与 Redis；编写 13 项 pytest 测试覆盖 Agent Loop、并发 RAG、Memory 隔离及 API 契约，并完成 DeepSeek、BGE/Qdrant、SSE 与 MCP 真实链路验证。

## 紧凑版（版面不足时使用）

### AgentHub — 基于 LangGraph 的智能知识 Agent 平台　　2026.3–2026.9

**GitHub：** [https://github.com/kh1ye/AgentHub](https://github.com/kh1ye/AgentHub)

**项目简介：** 面向企业知识问答与多轮任务场景，构建集工具调用、私有知识检索、多会话记忆和流式响应于一体的智能 Agent 后端，打通“Agent 决策 → 工具执行 → 结果回传 → 继续推理”的执行闭环。

**技术栈：** Python / LangGraph / FastAPI / DeepSeek / RAG / BGE / Qdrant / Redis / MCP / Docker

**项目内容：**

1. 基于 LangGraph 构建 `Agent → Tool → Agent` 条件循环，使 DeepSeek 能够在直接回答、计算、RAG 与 Web Search 间动态路由，并返回工具轨迹和检索来源。
2. 实现文档解析、递归切分、BGE Embedding、Qdrant 持久化及 Top-K 检索链路，将 Retriever 封装为可按需调用的 Agent Tool。
3. 使用 `user_id + conversation_id` 实现 Redis 会话隔离与 TTL，基于 FastAPI 提供异步对话、文档上传和 SSE 流式接口，并接入 MCP stdio 工具协议。
4. 使用 Docker Compose 编排服务，编写 13 项测试覆盖 Agent、并发 RAG、Memory 与 API，并完成 DeepSeek、BGE/Qdrant、SSE、MCP 真实链路验证。

## 60 秒面试讲解

AgentHub 是一个面向知识问答场景的有状态 Agent 后端。请求进入 FastAPI 后，系统先按用户和会话 ID 加载 Redis 历史，再交给 LangGraph 执行。DeepSeek 可以直接回答，也可以生成结构化 Tool Call；ToolNode 执行计算、RAG 或 Web Search 后，将 ToolMessage 写回状态继续推理。文档会经过解析、递归切分和本地 BGE 向量化，保存到 Qdrant，知识检索只在模型判断需要时触发。接口最终返回答案、工具轨迹和来源，同时支持 SSE 流式输出。

## 面试展示证据

- `app/agent/graph.py`：LangGraph 条件循环。
- `app/rag/`：文档加载、切分、Embedding、Qdrant 与检索模块。
- `app/memory/redis_memory.py`：会话命名空间和 TTL。
- `app/api/`：普通对话、SSE 与文档接口。
- `tests/`：13 项 Agent、RAG、Memory 和 API 测试。
