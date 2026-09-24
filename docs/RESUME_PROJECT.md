# 简历项目经历

## 正式简历版

### AgentHub — 基于 LangGraph 的可扩展 Agent 工具编排平台　　2026.3–2026.9

**GitHub：** [https://github.com/kh1ye/AgentHub](https://github.com/kh1ye/AgentHub)

**项目简介：** 面向需要调用多类工具完成任务的 AI Agent 场景，针对传统单轮 LLM 应用工具逻辑硬编码、执行过程不可追踪、外部服务接入方式不统一等问题，设计并实现可扩展 Agent Runtime；打通“模型决策 → 工具调用 → 结果回写 → 再推理”的执行闭环，并以异步 API 对外提供可观察的流式服务。

**技术栈：** Python / LangGraph / LangChain / FastAPI / DeepSeek / Tool Calling / MCP / SSE / Redis / Qdrant / Docker

**项目内容：**

1. **LangGraph Agent Runtime：** 基于 StateGraph 与 ToolNode 构建 `Agent → Tool → Agent` 条件循环，使用统一 AgentState 管理消息和工具结果；支持模型直接结束或连续调用工具，并通过 `handle_tool_errors` 将工具异常纳入执行链路，避免单次工具失败直接中断 Agent。
2. **可插拔工具编排：** 以 LangChain BaseTool 统一工具输入输出约束，将计算器、知识检索与 Web Search 作为可注入工具集合绑定至 DeepSeek；由模型根据语义生成结构化 Tool Call，执行完成后将 ToolMessage 写回状态，并从最终状态解析工具轨迹与引用来源。
3. **MCP 外部工具接入：** 实现基于 stdio 的 MCP Client，通过初始化握手、`list_tools` 与 `call_tool` 完成外部服务发现和调用；提供独立天气 MCP Server 示例并完成真实协议联调，为后续接入文件系统、数据库等外部能力预留统一接口。
4. **异步服务与流式响应：** 使用 FastAPI 提供普通对话、SSE 流式对话、文档上传和健康检查接口；基于 AsyncCallbackHandler 与 asyncio.Queue 实时推送模型 Token，响应中同步返回工具名称和检索来源，便于前端展示 Agent 执行过程。
5. **运行状态与工程验证：** 使用 `user_id + conversation_id` 隔离 Redis 会话上下文，将 BGE/Qdrant RAG 作为知识工具接入 Runtime；通过统一配置工厂和 Docker Compose 管理模型、API 与 Redis，编写 13 项 pytest 测试覆盖图循环、工具调用、并发检索、会话隔离及 API 契约。

## 紧凑版（推荐放入一页简历）

### AgentHub — 基于 LangGraph 的可扩展 Agent 工具编排平台　　2026.3–2026.9

**GitHub：** [https://github.com/kh1ye/AgentHub](https://github.com/kh1ye/AgentHub)

**项目简介：** 面向多工具任务执行场景构建可扩展 Agent Runtime，解决工具逻辑硬编码、执行过程不可追踪和外部服务接入不统一等问题，打通“模型决策 → 工具执行 → 结果回写 → 再推理”的执行闭环。

**技术栈：** Python / LangGraph / FastAPI / DeepSeek / Tool Calling / MCP / SSE / Redis / Qdrant / Docker

**项目内容：**

1. 基于 LangGraph StateGraph 与 ToolNode 构建条件循环，通过统一状态驱动模型连续调用工具或结束任务，并返回工具轨迹及引用来源。
2. 将计算器、RAG 与 Web Search 抽象为可注入的 LangChain Tools，由 DeepSeek 生成结构化 Tool Call；支持工具异常回传，避免单次执行失败中断 Agent。
3. 实现 MCP stdio 客户端及示例服务，完成工具发现与统一调用；基于 FastAPI、AsyncCallbackHandler 和 SSE 实现异步 Agent API 与 Token 级流式输出。
4. 使用 Redis 隔离会话上下文，将 BGE/Qdrant 作为知识工具接入 Runtime；以 Docker Compose 管理服务，13 项测试覆盖图循环、工具调用、并发检索、会话隔离与 API。

## 与 MELO 项目的简历定位差异

- **MELO：** 研究型项目，重点是长期记忆机制、闭环更新策略和实验评测。
- **AgentHub：** 工程型项目，重点是 Agent Runtime、工具编排、协议接入、流式服务和软件质量。

## 60 秒面试讲解

AgentHub 的核心是一个可扩展的 Agent 执行引擎。请求进入 FastAPI 后，LangGraph 根据当前消息状态调用 DeepSeek；模型可以直接回答，也可以生成结构化 Tool Call。ToolNode 执行计算、知识检索或网络搜索，并把结果作为 ToolMessage 写回图中，模型基于工具结果继续推理，直到生成最终答案。系统还通过 MCP 接入外部工具，通过 SSE 实时返回 Token，并把 Redis 和 Qdrant 分别作为会话状态与知识工具的基础设施。

## 面试展示证据

- `app/agent/graph.py`：StateGraph 条件循环和工具注入。
- `app/agent/service.py`：状态解析、工具轨迹和 SSE Token 队列。
- `app/mcp/client.py`：MCP 工具发现与调用。
- `app/api/chat.py`：普通对话与 SSE 接口。
- `tests/`：13 项 Agent、工具、RAG、Memory 和 API 测试。
