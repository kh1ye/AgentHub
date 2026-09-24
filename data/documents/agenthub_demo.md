# AgentHub Demo Knowledge

AgentHub is an interview-oriented AI Agent backend. It uses LangGraph to model a
stateful agent loop instead of a single prompt-response call.

## LangGraph workflow

The demo explains the workflow as five logical stages:

1. Receive the user message.
2. Let the DeepSeek model decide whether a tool is required.
3. Execute calculator, knowledge search, or web search.
4. Put the tool result back into LangGraph state.
5. Generate the final grounded answer.

The graph can return directly when no tool is required. When a tool is selected,
the graph follows `agent -> tools -> agent` until the model produces a final answer.

## RAG design

Documents are parsed, split with a chunk size of 500 characters and an overlap of
80 characters, embedded locally with `BAAI/bge-small-zh-v1.5`, and stored in the
persistent Qdrant collection `agenthub_knowledge`. Retrieval returns the top four
chunks by default.

## Memory design

Short-term context is represented by the messages in the current LangGraph run.
Conversation history is stored under a Redis key with the format
`agenthub:{user_id}:{conversation_id}`. This keeps different users and different
conversations isolated.

