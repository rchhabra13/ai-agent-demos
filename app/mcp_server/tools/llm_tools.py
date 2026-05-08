from typing import Annotated
from mcp.server.fastmcp import FastMCP

from app.integrations import llm_client


def register(mcp: FastMCP, get_app_state) -> None:

    @mcp.tool(description="Send a prompt to the configured LLM and return the response.")
    async def ask_llm(
        prompt: Annotated[str, "The user message / question to send"],
        system: Annotated[str, "Optional system prompt"] = "",
        max_tokens: Annotated[int, "Maximum tokens in the response"] = 1024,
    ) -> str:
        state = get_app_state()
        response = await llm_client.complete(
            state["http_client"], prompt, system, max_tokens
        )
        return response
