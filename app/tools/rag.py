import json

from langchain_core.tools import tool


@tool
def knowledge_search(query: str) -> str:
    """Search the persistent local knowledge base for document-grounded facts."""

    from app.rag.retriever import get_rag_service

    matches = get_rag_service().search(query)
    if not matches:
        return json.dumps(
            {
                "query": query,
                "context": "No relevant local document was found.",
                "sources": [],
            },
            ensure_ascii=False,
        )

    context_blocks = []
    sources = []
    for index, match in enumerate(matches, start=1):
        source = match["source"]
        page = match.get("page")
        source_label = f"{source}#page={page + 1}" if page is not None else source
        context_blocks.append(f"[{index}] {source_label}\n{match['content']}")
        sources.append(
            {
                "source": source,
                "page": page,
                "score": match.get("score"),
            }
        )

    return json.dumps(
        {
            "query": query,
            "context": "\n\n".join(context_blocks),
            "sources": sources,
        },
        ensure_ascii=False,
    )

