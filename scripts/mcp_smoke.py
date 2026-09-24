import asyncio
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.mcp.client import MCPClient


async def main() -> None:
    client = MCPClient()
    tools = await client.list_tools()
    print(json.dumps(tools, ensure_ascii=False, indent=2))
    result = await client.call_tool("weather", {"city": "Shanghai"})
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

