import json

import httpx
from langchain_core.tools import tool


WIKIPEDIA_API = "https://zh.wikipedia.org/w/api.php"


@tool
def web_search(query: str) -> str:
    """Search current public web knowledge when local documents are insufficient."""

    with httpx.Client(
        timeout=10.0,
        headers={"User-Agent": "AgentHub/0.1 (interview project)"},
    ) as client:
        response = client.get(
            WIKIPEDIA_API,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 3,
                "format": "json",
                "utf8": 1,
                "origin": "*",
            },
        )
        response.raise_for_status()

    records = []
    for item in response.json().get("query", {}).get("search", []):
        title = item["title"]
        records.append(
            {
                "title": title,
                "snippet": item.get("snippet", ""),
                "url": f"https://zh.wikipedia.org/wiki/{title.replace(' ', '_')}",
            }
        )
    return json.dumps({"query": query, "results": records}, ensure_ascii=False)

