# AgentHub Interview Guide

## 1. LangChain and LangGraph

LangChain provides model, prompt, Tool, retriever, and runnable abstractions.
LangGraph adds an explicit state machine for long-running or cyclic workflows.
AgentHub uses LangChain Tools and messages inside a LangGraph `StateGraph`.

## 2. Agent versus ordinary LLM call

An ordinary call maps messages directly to one model response. An Agent can inspect
the task, select tools, observe results, update state, and repeat until it can answer.

## 3. Tool Calling

`bind_tools()` converts Python tool schemas into definitions understood by the
model. DeepSeek returns a tool name and structured arguments. `ToolNode` validates
and executes the call, then adds a `ToolMessage` to state.

## 4. ReAct

ReAct interleaves reasoning and actions: decide an action, observe its result, and
continue reasoning. AgentHub implements the observable action loop without exposing
private chain-of-thought; tool calls and ToolMessages are the inspectable trace.

## 5. Agent Loop

The graph starts at `agent`. `tools_condition` checks the last AIMessage. With tool
calls it routes to `tools`, then back to `agent`; otherwise it routes to END.

## 6. Complete RAG flow

PDF/TXT/Markdown is parsed into Documents, recursively split, embedded with local
BGE, persisted in Qdrant, retrieved with top-k similarity search, and returned to
the model through `knowledge_search`.

## 7. Why chunk overlap

Semantic content can cross a hard chunk boundary. An 80-character overlap keeps
boundary context in both neighboring chunks. Excessive overlap wastes storage and
creates duplicate retrieval results.

## 8. How top-k was selected

AgentHub defaults to four chunks. It is large enough to cover neighboring evidence
but small enough to limit noise and prompt cost. In production it should be tuned on
a labeled retrieval set using Recall@K and downstream answer quality.

## 9. Vector database role

Qdrant stores vectors, metadata, and source text, then performs approximate or exact
similarity search. Local persistent mode makes the interview project self-contained;
a remote Qdrant service can replace it later.

## 10. Embeddings

An embedding maps text into a dense numeric vector where semantically related text
has similar geometry. AgentHub separates local BGE embeddings from DeepSeek text
generation so document indexing does not consume a paid generation API.

## 11. Why Redis for Memory

Redis offers low-latency key access, JSON-compatible string storage, TTL, and a
simple key namespace. The key combines user and conversation IDs, which prevents
different sessions from sharing history.

## 12. Short-term and long-term memory

Short-term state is the message list in one LangGraph execution. Conversation memory
is stored across HTTP requests in Redis. This release stores user and final assistant
messages; summarization and user-profile extraction are later extensions.

## 13. MCP

An application-local LangChain Tool is registered directly in code. MCP defines a
standard protocol for discovering and calling external tools/resources/prompts.
AgentHub includes an optional stdio client and demo server while keeping core chat
independent from MCP availability.

## 14. SSE versus WebSocket

SSE is a one-way HTTP stream and fits server-to-client token delivery with simple
reconnection semantics. WebSocket is bidirectional and better when both sides need
continuous events. AgentHub uses ordinary POST input and SSE output.

## 15. FastAPI async

Endpoints are async so uploads and streams do not block the event loop. Existing
synchronous LangChain/Qdrant work is moved through `run_in_threadpool`; streaming
uses the graph's async invocation and an async token queue.

## 16. Failure handling and observability

Tool execution errors are returned to the Agent by `ToolNode(handle_tool_errors=True)`.
The health endpoint avoids network calls. Useful production additions include
structured logs, request IDs, tool latency, token usage, retrieval scores, and traces.

## 17. What would be improved next

- Labeled retrieval evaluation and reranking.
- Conversation summarization and structured user profiles.
- Authentication, rate limiting, and upload authorization.
- Remote Qdrant and Redis high availability.
- Agent execution limits, timeouts, and human approval for risky tools.

