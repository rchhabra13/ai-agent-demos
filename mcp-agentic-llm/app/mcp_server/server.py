"""
MCP server definition. Tools are registered here and the server exposes
two ASGI apps that get mounted into the main FastAPI application.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-agentic-server")

# _app_state is set by main.py after startup so tools can access
# the shared httpx client, Redis connection, and current session.
_app_state: dict = {}


def set_app_state(state: dict) -> None:
    global _app_state
    _app_state = state


def get_app_state() -> dict:
    return _app_state


def _get_session():
    from app.crud.database import async_session_factory
    return async_session_factory()


def register_tools() -> None:
    from app.mcp_server.tools import github_tools, crud_tools, llm_tools

    github_tools.register(mcp, get_app_state)
    crud_tools.register(mcp, _get_session)
    llm_tools.register(mcp, get_app_state)
