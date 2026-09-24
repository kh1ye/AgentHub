from mcp.server.fastmcp import FastMCP


mcp = FastMCP("agenthub-demo")


@mcp.tool()
def weather(city: str) -> str:
    """Return deterministic demo weather without calling an external service."""

    return f"{city}: sunny, 25 C (demo data)"


if __name__ == "__main__":
    mcp.run(transport="stdio")

