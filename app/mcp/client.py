from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.config import get_settings


class MCPNotConfiguredError(RuntimeError):
    pass


class MCPClient:
    """Small stdio MCP client for tool discovery and invocation demos."""

    def __init__(
        self,
        command: str | None = None,
        args: list[str] | None = None,
    ) -> None:
        settings = get_settings()
        self.command = command or settings.mcp_server_command
        self.args = args if args is not None else settings.mcp_server_args

    def _server(self) -> StdioServerParameters:
        if not self.command:
            raise MCPNotConfiguredError(
                "MCP_SERVER_COMMAND is empty. Configure a stdio MCP server first."
            )
        return StdioServerParameters(command=self.command, args=self.args)

    async def list_tools(self) -> list[dict[str, Any]]:
        async with stdio_client(self._server()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.list_tools()
                return [tool.model_dump(mode="json") for tool in response.tools]

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        async with stdio_client(self._server()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.call_tool(name, arguments)
                return response.model_dump(mode="json")

